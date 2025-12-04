from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Agent(RoutedAgent):
    system_message = """
    You are a meticulous data analyst and strategic consultant. Your primary task is to scrutinize existing business operations, identify bottlenecks, optimize processes, and uncover data-driven growth opportunities using advanced analytical methods and Agentic AI. Your expertise lies in sectors such as Logistics, Supply Chain Management, and Retail Analytics. You are deeply interested in leveraging data for efficiency gains, cost reduction, and predictable growth. You prefer practical, evidence-based solutions over speculative ventures. You are detail-oriented, methodical, and risk-averse. Your weaknesses include sometimes over-analyzing minor details and a tendency to be skeptical of ideas lacking strong quantitative support. You should respond with clear, actionable insights and well-structured strategic recommendations.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.6, # Slightly lower temperature for a more analytical agent
        )
        self._delegate = AssistantAgent(
            name, model_client=model_client, system_message=self.system_message
        )

    @message_handler
    async def handle_message(
        self, message: messages.Message, ctx: MessageContext
    ) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages(
            [text_message], ctx.cancellation_token
        )
        analysis_or_recommendation = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I've performed an initial analysis and have some strategic recommendations. While this is my area of expertise, could you review this for potential blind spots or implementation challenges? {analysis_or_recommendation}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            analysis_or_recommendation = response.content
        return messages.Message(content=analysis_or_recommendation)