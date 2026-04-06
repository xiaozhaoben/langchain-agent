from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts


@wrap_tool_call
def monitor_tool(
        # 请求的数据封装
        request: ToolCallRequest,
        # 执行的函数本身
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command:
    logger.info(f"[monitor_tool] 执行工具: {request.tool_call['name']}")
    logger.info(f"[monitor_tool] 传入参数: {request.tool_call['args']}")
    try:
        result = handler(request)

        logger.info(f"[monitor_tool] 工具{request.tool_call['name']}调用成功")
        if request.tool_call['name'] == 'fill_context_for_report':
            request.runtime.context['report'] = True
        return result
    except Exception as e:
        logger.error(f"[monitor_tool] 工具{request.tool_call['name']}调用失败, {str(e)}")
        raise e

@before_model
def log_before_model(
        state: AgentState, # 整个 Agent 智能体的状态记录
        runtime: Runtime # 记录整个执行过程的上下文
):
    logger.info(f"[log_before_model] 即将调用模型，带有{len(state['messages'])}条消息")
    
    if state['messages']:
        last_msg = state['messages'][-1]
        content = last_msg.content if hasattr(last_msg, 'content') and last_msg.content else ''
        logger.debug(f"[log_before_model] {type(last_msg).__name__} | {content.strip()}")
    return None

@dynamic_prompt  # 每次在生成提示词之前调用
def report_prompt_switch(request: ModelRequest): # 动态切换提示词
    is_report = request.runtime.context.get('report', False)
    if is_report:  # 返回报告提示词
        return load_report_prompts()

    return load_system_prompts()