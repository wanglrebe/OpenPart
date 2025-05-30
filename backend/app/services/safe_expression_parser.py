# backend/app/services/safe_expression_parser.py
"""
安全表达式解析器

提供安全的表达式解析、验证和执行功能，防止代码注入和恶意操作
"""

import ast
import operator
import hashlib
import time
import re
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.compatibility import ExpressionSecurityCache, create_expression_hash
from app.schemas.compatibility import SecurityValidationResponse, RiskLevel
import logging

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """安全错误异常"""
    pass

class ExpressionError(Exception):
    """表达式错误异常"""
    pass

class SafeExpressionEngine:
    """安全表达式引擎"""
    
    def __init__(self):
        self.setup_security_rules()
        self.setup_safe_environment()
    
    def setup_security_rules(self):
        """设置安全规则"""
        
        # 允许的AST节点类型（白名单）
        self.allowed_nodes = {
            # 基本表达式
            ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare,
            # 数据类型
            ast.Constant, ast.List, ast.Tuple, ast.Dict, ast.Set,
            # 变量和属性
            ast.Name, ast.Attribute, ast.Subscript,
            # 控制结构（限制性允许）
            ast.IfExp,  # 三元表达式
            # 函数调用（受限）
            ast.Call,
            # 操作符
            ast.And, ast.Or, ast.Not,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
            ast.In, ast.NotIn, ast.Is, ast.IsNot
        }
        
        # 添加兼容性节点（如果存在的话）
        if hasattr(ast, 'Num'):
            self.allowed_nodes.add(ast.Num)
        if hasattr(ast, 'Str'):
            self.allowed_nodes.add(ast.Str)
        if hasattr(ast, 'NameConstant'):
            self.allowed_nodes.add(ast.NameConstant)
        if hasattr(ast, 'Index'):
            self.allowed_nodes.add(ast.Index)
        if hasattr(ast, 'Slice'):
            self.allowed_nodes.add(ast.Slice)
        
        # 禁用的AST节点类型（黑名单）
        self.forbidden_nodes = {
            # 导入和执行
            ast.Import, ast.ImportFrom,
            # 函数和类定义
            ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef,
            # 控制流
            ast.For, ast.While, ast.If, ast.With, ast.AsyncWith,
            # 异常处理
            ast.Try, ast.Raise, ast.Assert,
            # 赋值和删除
            ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Delete,
            # 生成器和推导式
            ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp,
            # 异步相关
            ast.Await, ast.AsyncFor, ast.AsyncWith,
            # 其他危险操作
            ast.Global, ast.Nonlocal, ast.Return, ast.Yield, ast.YieldFrom
        }
        
        # 添加兼容性检查（如果存在的话）
        if hasattr(ast, 'Exec'):
            self.forbidden_nodes.add(ast.Exec)
        if hasattr(ast, 'Eval'):
            self.forbidden_nodes.add(ast.Eval)
        
        # 允许的内置函数（白名单）
        self.allowed_functions = {
            # 数学函数
            'abs', 'min', 'max', 'sum', 'round',
            # 类型转换
            'int', 'float', 'str', 'bool',
            # 序列操作
            'len', 'range', 'enumerate', 'zip',
            # 逻辑函数
            'all', 'any',
            # 自定义安全函数
            'safe_get', 'safe_contains', 'safe_match'
        }
        
        # 禁用的内置函数/属性（黑名单）
        self.forbidden_functions = {
            # 执行相关
            'eval', 'exec', 'compile', '__import__', 'reload',
            # 文件操作
            'open', 'file', 'input', 'raw_input',
            # 系统操作
            'exit', 'quit', 'help', 'license', 'credits',
            # 反射操作
            'getattr', 'setattr', 'delattr', 'hasattr',
            'globals', 'locals', 'vars', 'dir',
            # 危险属性
            '__class__', '__bases__', '__subclasses__', '__mro__',
            '__globals__', '__code__', '__func__', '__self__',
            '__builtins__', '__import__', '__file__', '__name__'
        }
        
        # 危险字符串模式
        self.dangerous_patterns = [
            r'__.*__',  # 双下划线属性
            r'eval\s*\(',  # eval调用
            r'exec\s*\(',  # exec调用
            r'import\s+',  # import语句
            r'subprocess',  # subprocess模块
            r'os\.system',  # os.system调用
            r'open\s*\(',  # 文件打开
        ]
    
    def setup_safe_environment(self):
        """设置安全执行环境"""
        
        # 安全的内置函数环境
        self.safe_builtins = {
            # 数学运算
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'round': round,
            
            # 类型转换
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            
            # 序列操作
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            
            # 逻辑函数
            'all': all,
            'any': any,
            
            # 安全辅助函数
            'safe_get': self._safe_get,
            'safe_contains': self._safe_contains,
            'safe_match': self._safe_match,
        }
        
        # 安全的操作符映射
        self.safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.BitAnd: operator.and_,
            ast.FloorDiv: operator.floordiv,
            
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
            
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.Is: operator.is_,
            ast.IsNot: operator.is_not,
            ast.In: lambda x, y: x in y,
            ast.NotIn: lambda x, y: x not in y,
            
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Not: operator.not_,
            ast.Invert: operator.invert,
        }

    async def validate_expression_security(
        self, 
        expression: str, 
        db: Optional[Session] = None
    ) -> SecurityValidationResponse:
        """
        验证表达式安全性
        
        Args:
            expression: 要验证的表达式
            db: 数据库会话（可选，用于缓存）
            
        Returns:
            SecurityValidationResponse: 安全验证结果
        """
        
        try:
            # 检查缓存
            if db:
                cached_result = await self._get_cached_security_result(expression, db)
                if cached_result:
                    return cached_result
            
            # 执行安全检查
            security_issues = []
            risk_level = RiskLevel.LOW
            recommendations = []
            
            # 1. 字符串模式检查
            pattern_issues = self._check_dangerous_patterns(expression)
            security_issues.extend(pattern_issues)
            
            # 2. AST语法树检查
            try:
                tree = ast.parse(expression, mode='eval')
                ast_issues = self._check_ast_security(tree)
                security_issues.extend(ast_issues)
            except SyntaxError as e:
                security_issues.append({
                    "type": "syntax_error",
                    "message": f"语法错误: {str(e)}",
                    "severity": "high"
                })
            
            # 3. 计算风险等级
            risk_level = self._calculate_risk_level(security_issues)
            
            # 4. 生成建议
            recommendations = self._generate_security_recommendations(security_issues)
            
            is_safe = risk_level != RiskLevel.HIGH and len([
                issue for issue in security_issues 
                if issue.get("severity") == "high"
            ]) == 0
            
            result = SecurityValidationResponse(
                is_safe=is_safe,
                security_issues=security_issues,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            # 缓存结果
            if db:
                await self._cache_security_result(expression, result, db)
            
            return result
            
        except Exception as e:
            logger.error(f"安全验证失败: {str(e)}")
            return SecurityValidationResponse(
                is_safe=False,
                security_issues=[{
                    "type": "validation_error",
                    "message": f"验证过程出错: {str(e)}",
                    "severity": "high"
                }],
                risk_level=RiskLevel.HIGH,
                recommendations=["表达式验证失败，请检查语法"]
            )

    async def execute_safe_expression(
        self, 
        expression: str, 
        context: Dict[str, Any]
    ) -> Any:
        """
        安全执行表达式
        
        Args:
            expression: 要执行的表达式
            context: 执行上下文
            
        Returns:
            表达式执行结果
        """
        
        try:
            # 先进行安全验证
            validation_result = await self.validate_expression_security(expression)
            if not validation_result.is_safe:
                high_risk_issues = [
                    issue for issue in validation_result.security_issues 
                    if issue.get("severity") == "high"
                ]
                raise SecurityError(f"表达式存在安全风险: {high_risk_issues}")
            
            # 解析表达式
            tree = ast.parse(expression, mode='eval')
            
            # 准备安全执行环境
            safe_context = self._prepare_safe_context(context)
            
            # 执行表达式
            result = self._eval_node(tree.body, safe_context)
            
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            logger.error(f"表达式执行失败: {str(e)}")
            raise ExpressionError(f"表达式执行失败: {str(e)}")

    def _check_dangerous_patterns(self, expression: str) -> List[Dict[str, Any]]:
        """检查危险字符串模式"""
        
        issues = []
        
        for pattern in self.dangerous_patterns:
            matches = re.finditer(pattern, expression, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "dangerous_pattern",
                    "message": f"发现危险模式: {match.group()}",
                    "pattern": pattern,
                    "position": match.span(),
                    "severity": "high"
                })
        
        return issues

    def _check_ast_security(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """检查AST语法树安全性"""
        
        issues = []
        
        for node in ast.walk(tree):
            node_type = type(node)
            
            # 检查禁用节点
            if node_type in self.forbidden_nodes:
                issues.append({
                    "type": "forbidden_node",
                    "message": f"禁止使用的语法: {node_type.__name__}",
                    "node_type": node_type.__name__,
                    "severity": "high"
                })
            
            # 检查函数调用
            if isinstance(node, ast.Call):
                func_issues = self._check_function_call_security(node)
                issues.extend(func_issues)
            
            # 检查属性访问
            if isinstance(node, ast.Attribute):
                attr_issues = self._check_attribute_access_security(node)
                issues.extend(attr_issues)
        
        return issues

    def _check_function_call_security(self, node: ast.Call) -> List[Dict[str, Any]]:
        """检查函数调用安全性"""
        
        issues = []
        
        # 获取函数名
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name:
            # 检查是否为禁用函数
            if func_name in self.forbidden_functions:
                issues.append({
                    "type": "forbidden_function",
                    "message": f"禁止调用函数: {func_name}",
                    "function_name": func_name,
                    "severity": "high"
                })
            
            # 检查是否为未授权函数
            elif func_name not in self.allowed_functions:
                issues.append({
                    "type": "unauthorized_function",
                    "message": f"未授权的函数调用: {func_name}",
                    "function_name": func_name,
                    "severity": "medium"
                })
        
        return issues

    def _check_attribute_access_security(self, node: ast.Attribute) -> List[Dict[str, Any]]:
        """检查属性访问安全性"""
        
        issues = []
        
        attr_name = node.attr
        
        # 检查危险属性
        if attr_name in self.forbidden_functions:
            issues.append({
                "type": "dangerous_attribute",
                "message": f"禁止访问属性: {attr_name}",
                "attribute_name": attr_name,
                "severity": "high"
            })
        
        # 检查双下划线属性
        if attr_name.startswith('__') and attr_name.endswith('__'):
            issues.append({
                "type": "dunder_attribute",
                "message": f"禁止访问特殊属性: {attr_name}",
                "attribute_name": attr_name,
                "severity": "high"
            })
        
        return issues

    def _calculate_risk_level(self, security_issues: List[Dict[str, Any]]) -> RiskLevel:
        """计算风险等级"""
        
        high_count = len([i for i in security_issues if i.get("severity") == "high"])
        medium_count = len([i for i in security_issues if i.get("severity") == "medium"])
        
        if high_count > 0:
            return RiskLevel.HIGH
        elif medium_count > 2:
            return RiskLevel.MEDIUM
        elif medium_count > 0 or len(security_issues) > 0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_security_recommendations(
        self, 
        security_issues: List[Dict[str, Any]]
    ) -> List[str]:
        """生成安全建议"""
        
        recommendations = []
        
        issue_types = {issue.get("type") for issue in security_issues}
        
        if "forbidden_function" in issue_types:
            recommendations.append("移除禁用的函数调用，使用允许的安全函数")
        
        if "dangerous_pattern" in issue_types:
            recommendations.append("避免使用危险的字符串模式")
        
        if "forbidden_node" in issue_types:
            recommendations.append("简化表达式，只使用基本的比较和逻辑操作")
        
        if "unauthorized_function" in issue_types:
            recommendations.append("只使用预定义的安全函数")
        
        if not recommendations:
            recommendations.append("表达式安全性良好")
        
        return recommendations

    def _prepare_safe_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """准备安全执行上下文"""
        
        safe_context = {
            '__builtins__': self.safe_builtins.copy()
        }
        
        # 添加用户提供的上下文，但进行安全过滤
        for key, value in context.items():
            if not key.startswith('__') and key not in self.forbidden_functions:
                safe_context[key] = value
        
        return safe_context

    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Any:
        """递归评估AST节点"""
        
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, (ast.Num, ast.Str, ast.NameConstant)):  # 兼容旧版本
            return node.n if hasattr(node, 'n') else (node.s if hasattr(node, 's') else node.value)
        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            elif node.id in self.safe_builtins:
                return self.safe_builtins[node.id]
            else:
                raise NameError(f"未定义的变量: {node.id}")
        elif isinstance(node, ast.Attribute):
            obj = self._eval_node(node.value, context)
            attr_name = node.attr
            
            # 安全检查
            if attr_name.startswith('__') or attr_name in self.forbidden_functions:
                raise SecurityError(f"禁止访问属性: {attr_name}")
            
            # 处理字典类型的属性访问
            if isinstance(obj, dict):
                value = obj.get(attr_name)
                if value is None:
                    # 提供更友好的错误信息
                    available_keys = list(obj.keys())
                    raise AttributeError(f"属性 '{attr_name}' 不存在。可用属性: {available_keys}")
                return value
            else:
                if not hasattr(obj, attr_name):
                    raise AttributeError(f"对象没有属性 '{attr_name}'")
                return getattr(obj, attr_name)
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op_type = type(node.op)
            
            if op_type in self.safe_operators:
                return self.safe_operators[op_type](left, right)
            else:
                raise SecurityError(f"不支持的二元操作: {op_type.__name__}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op_type = type(node.op)
            
            if op_type in self.safe_operators:
                return self.safe_operators[op_type](operand)
            else:
                raise SecurityError(f"不支持的一元操作: {op_type.__name__}")
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context)
                op_type = type(op)
                
                if op_type in self.safe_operators:
                    result = self.safe_operators[op_type](left, right)
                    if not result:
                        return False
                    left = right  # 链式比较
                else:
                    raise SecurityError(f"不支持的比较操作: {op_type.__name__}")
            
            return True
        elif isinstance(node, ast.BoolOp):
            values = [self._eval_node(value, context) for value in node.values]
            
            if isinstance(node.op, ast.And):
                return all(values)
            elif isinstance(node.op, ast.Or):
                return any(values)
            else:
                raise SecurityError(f"不支持的布尔操作: {type(node.op).__name__}")
        elif isinstance(node, ast.Call):
            return self._eval_function_call(node, context)
        elif isinstance(node, ast.List):
            return [self._eval_node(item, context) for item in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(item, context) for item in node.elts)
        elif isinstance(node, ast.Dict):
            return {
                self._eval_node(k, context): self._eval_node(v, context)
                for k, v in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.Subscript):
            obj = self._eval_node(node.value, context)
            
            # 处理索引（兼容Python 3.8-）
            if hasattr(node.slice, 'value'):  # Python < 3.9
                index = self._eval_node(node.slice.value, context)
            else:  # Python >= 3.9
                index = self._eval_node(node.slice, context)
            
            return obj[index]
        elif isinstance(node, ast.IfExp):  # 三元表达式
            test = self._eval_node(node.test, context)
            if test:
                return self._eval_node(node.body, context)
            else:
                return self._eval_node(node.orelse, context)
        else:
            raise SecurityError(f"不支持的节点类型: {type(node).__name__}")

    def _eval_function_call(self, node: ast.Call, context: Dict[str, Any]) -> Any:
        """评估函数调用"""
        
        # 获取函数对象
        func = self._eval_node(node.func, context)
        
        # 检查函数是否安全
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name and func_name not in self.allowed_functions:
            raise SecurityError(f"不允许调用函数: {func_name}")
        
        # 评估参数
        args = [self._eval_node(arg, context) for arg in node.args]
        kwargs = {
            kw.arg: self._eval_node(kw.value, context) 
            for kw in node.keywords
        }
        
        # 调用函数
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ExpressionError(f"函数调用失败 {func_name}: {str(e)}")

    # ==================== 安全辅助函数 ====================

    def _safe_get(self, obj: Any, key: str, default: Any = 0) -> Any:
        """安全获取对象属性或字典值 - 改进版本"""
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            elif hasattr(obj, key) and not key.startswith('__'):
                return getattr(obj, key, default)
            else:
                return default
        except:
            return default

    def _safe_contains(self, container: Any, item: Any) -> bool:
        """安全检查包含关系"""
        try:
            return item in container
        except:
            return False

    def _safe_match(self, text: str, pattern: str) -> bool:
        """安全的字符串匹配（简单模式）"""
        try:
            if not isinstance(text, str) or not isinstance(pattern, str):
                return False
            
            # 只支持简单的通配符匹配，不支持正则表达式
            import fnmatch
            return fnmatch.fnmatch(text.lower(), pattern.lower())
        except:
            return False

    # ==================== 缓存相关方法 ====================

    async def _get_cached_security_result(
        self, 
        expression: str, 
        db: Session
    ) -> Optional[SecurityValidationResponse]:
        """获取缓存的安全验证结果"""
        
        try:
            expression_hash = create_expression_hash(expression)
            
            cached = db.query(ExpressionSecurityCache).filter(
                ExpressionSecurityCache.expression_hash == expression_hash
            ).first()
            
            if cached:
                # 检查缓存是否过期（24小时）
                cache_age = datetime.utcnow() - cached.scanned_at
                if cache_age.total_seconds() < 86400:  # 24小时
                    return SecurityValidationResponse(
                        is_safe=cached.is_safe,
                        security_issues=cached.security_issues or [],
                        risk_level=RiskLevel.LOW if cached.is_safe else RiskLevel.HIGH,
                        recommendations=[]
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"获取安全缓存失败: {str(e)}")
            return None

    async def _cache_security_result(
        self, 
        expression: str, 
        result: SecurityValidationResponse, 
        db: Session
    ):
        """缓存安全验证结果"""
        
        try:
            expression_hash = create_expression_hash(expression)
            
            # 删除旧缓存
            db.query(ExpressionSecurityCache).filter(
                ExpressionSecurityCache.expression_hash == expression_hash
            ).delete()
            
            # 创建新缓存
            cache_entry = ExpressionSecurityCache(
                expression_hash=expression_hash,
                expression_text=expression,
                is_safe=result.is_safe,
                security_issues=result.security_issues
            )
            
            db.add(cache_entry)
            db.commit()
            
        except Exception as e:
            logger.warning(f"缓存安全结果失败: {str(e)}")
            db.rollback()

    # ==================== 工具方法 ====================

    def get_allowed_functions(self) -> List[str]:
        """获取允许的函数列表"""
        return sorted(list(self.allowed_functions))

    def get_function_help(self, func_name: str) -> Optional[str]:
        """获取函数帮助信息"""
        
        help_texts = {
            'abs': '绝对值函数，返回数字的绝对值',
            'min': '最小值函数，返回序列中的最小值',
            'max': '最大值函数，返回序列中的最大值',
            'sum': '求和函数，计算序列中所有元素的和',
            'round': '四舍五入函数，将数字四舍五入到指定小数位',
            'len': '长度函数，返回序列的长度',
            'range': '范围函数，生成数字序列',
            'all': '全真函数，当序列中所有元素都为真时返回True',
            'any': '存真函数，当序列中存在真值元素时返回True',
            'safe_get': '安全获取函数，safe_get(对象, "属性名", 默认值)',
            'safe_contains': '安全包含检查，safe_contains(容器, 元素)',
            'safe_match': '安全模式匹配，safe_match("文本", "模式")'
        }
        
        return help_texts.get(func_name)

    def validate_expression_syntax(self, expression: str) -> Dict[str, Any]:
        """验证表达式语法"""
        
        try:
            ast.parse(expression, mode='eval')
            return {
                "valid": True,
                "message": "语法正确"
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "message": f"语法错误: {str(e)}",
                "line": e.lineno,
                "offset": e.offset
            }

    def get_expression_dependencies(self, expression: str) -> List[str]:
        """获取表达式依赖的变量名"""
        
        try:
            tree = ast.parse(expression, mode='eval')
            dependencies = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id not in self.safe_builtins:
                    dependencies.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # 递归获取根对象名称
                    root = node
                    while isinstance(root.value, ast.Attribute):
                        root = root.value
                    if isinstance(root.value, ast.Name):
                        dependencies.add(root.value.id)
            
            return sorted(list(dependencies))
            
        except Exception as e:
            logger.warning(f"获取表达式依赖失败: {str(e)}")
            return []

    async def cleanup_expired_cache(self, db: Session):
        """清理过期的安全缓存"""
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=7)  # 7天前
            
            deleted_count = db.query(ExpressionSecurityCache).filter(
                ExpressionSecurityCache.scanned_at < cutoff_time
            ).delete()
            
            db.commit()
            
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 个过期的安全缓存条目")
            
        except Exception as e:
            logger.error(f"清理安全缓存失败: {str(e)}")
            db.rollback()


# 示例用法和测试
if __name__ == "__main__":
    import asyncio
    
    async def test_safe_expression_engine():
        engine = SafeExpressionEngine()
        
        # 测试安全表达式
        safe_expressions = [
            "part_a.voltage == part_b.voltage",
            "part_a.length <= part_b.max_length and part_a.width <= part_b.max_width",
            "sum([part_a.power, part_b.power]) <= 1000",
            "len(part_a.name) > 0",
            "safe_get(part_a, 'category', '') == 'CPU'"
        ]
        
        # 测试危险表达式
        dangerous_expressions = [
            "__import__('os').system('ls')",
            "eval('malicious_code')",
            "open('/etc/passwd').read()",
            "part_a.__class__.__bases__"
        ]
        
        print("=== 测试安全表达式 ===")
        for expr in safe_expressions:
            try:
                result = await engine.validate_expression_security(expr)
                print(f"✓ {expr[:50]}... -> 安全: {result.is_safe}")
            except Exception as e:
                print(f"✗ {expr[:50]}... -> 错误: {str(e)}")
        
        print("\n=== 测试危险表达式 ===")
        for expr in dangerous_expressions:
            try:
                result = await engine.validate_expression_security(expr)
                print(f"{'✓' if not result.is_safe else '✗'} {expr[:50]}... -> 安全: {result.is_safe}")
            except Exception as e:
                print(f"✗ {expr[:50]}... -> 错误: {str(e)}")
        
        print("\n=== 测试表达式执行 ===")
        context = {
            'part_a': {
                'voltage': 12,
                'length': 100,
                'width': 50,
                'name': 'Test Part A'
            },
            'part_b': {
                'voltage': 12,
                'max_length': 120,
                'max_width': 60,
                'name': 'Test Part B'
            }
        }
        
        for expr in safe_expressions:
            try:
                result = await engine.execute_safe_expression(expr, context)
                print(f"✓ {expr} -> {result}")
            except Exception as e:
                print(f"✗ {expr} -> 错误: {str(e)}")
    
    # 运行测试
    asyncio.run(test_safe_expression_engine())