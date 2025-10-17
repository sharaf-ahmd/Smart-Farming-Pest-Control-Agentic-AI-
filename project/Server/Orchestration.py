from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import util
from PIL import Image


load_dotenv()

# Initialize util artifacts
print("Loading models and artifacts...")
util.load_saved_artifacts()
print("✅ All artifacts loaded successfully!\n")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Tool definitions
@tool("pestDetector")
def pestAgent(image_path: str) -> str:
    """Detects pest using image uploaded by the user. Pass the image file path."""
    try:
        img = Image.open(image_path)
        result = util.get_prediction(img)
        return f"Pest Detection Results: {result}"
    except Exception as e:
        return f"Error detecting pest: {str(e)}"


@tool("impactAnalyzer")
def impactagent(pest: str, crop: str) -> str:
    """Predicts the impact/risk caused by the pest to the crop"""
    try:
        result = util.analyze(pest, crop)
        return result
    except Exception as e:
        return f"Error analyzing impact: {str(e)}"


@tool("treatmentRecommendor")
def treatmentagent(pest: str, crop: str) -> str:
    """Provides treatment recommendation for the crops"""
    try:
        result = util.reccomend(pest, crop)
        return result
    except Exception as e:
        return f"Error getting treatment recommendation: {str(e)}"


tools = [pestAgent, impactagent, treatmentagent]

system_prompt = SystemMessage(
    content=(
        "You are AgriGuard AI, an expert agricultural assistant. "
        "Use the available tools to help farmers with pest management. "
        "\n\nIMPORTANT RULES:"
        "\n1. ONLY use pestDetector tool when the user has explicitly provided an image path (look for 'Image path:' in the message)"
        "\n2. If user mentions bugs/pests without an image, ask them to upload an image for accurate identification"
        "\n3. If user already knows the pest name, skip pestDetector and directly use impactAnalyzer or treatmentRecommendor"
        "\n4. After detecting pests with pestDetector, use impactAnalyzer to assess damage"
        "\n5. Use treatmentRecommendor to suggest solutions based on the pest and crop"
        "\n6. If critical information (pest name, crop type, or image) is missing, ask the user politely"
    )
)

model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)



def agent_node(state: AgentState) -> AgentState:
    """Agent reasoning node - processes messages and decides tool usage"""
    messages = [system_prompt] + list(state["messages"])
    response = model.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Decide whether to continue with tools or end the workflow"""
    last_message = state["messages"][-1]
    
    # Check for tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end the workflow
    return "end"



graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    },
)

graph.add_edge("tools", "agent")
app = graph.compile()


# Helper functions for running the agent
def run_agent(user_query: str):
    """
    Run the agent with a single user query
    
    Args:
        user_query: The user's question or request
        
    Returns:
        The final AI response
    """
    initial_state = {
        "messages": [HumanMessage(content=user_query)]
    }
    
    result = app.invoke(initial_state)
    
    # Return the last AI message
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    
    return "No response generated"


def run_interactive():
    """Run the agent in interactive mode"""
    print("\n" + "="*60)
    print("🌾 AGRIGUARD AI - Interactive Mode")
    print("="*60)
    print("Type 'exit', 'quit', or 'bye' to end the conversation\n")
    
    messages = []
    
    while True:
        user_input = input("\n🌾 You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\n👋 Goodbye! Happy farming!")
            break
        
        if not user_input:
            continue
        
        # Add user message
        messages.append(HumanMessage(content=user_input))
        
        # Invoke the agent
        state = {"messages": messages}
        result = app.invoke(state)
        
        # Update messages with the full conversation
        messages = result["messages"]
        
        # Print the AI's response
        last_message = messages[-1]
        if isinstance(last_message, AIMessage) and last_message.content:
            print(f"\n🤖 AgriGuard AI: {last_message.content}")


if __name__ == "__main__":
    run_interactive()
