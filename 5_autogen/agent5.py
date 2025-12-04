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
    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a meticulous Financial Analyst and Market Strategist. Your primary task is to thoroughly analyze market trends, evaluate potential investment opportunities, or assess the viability and financial projections of new business concepts.
    Your personal interests are deeply rooted in Fintech, E-commerce, and optimizing Supply Chain Logistics.
    You are driven by data, preferring evidence-based insights and a pragmatic approach to problem-solving. While you appreciate innovation, you are inherently risk-averse and prioritize financial stability and clear return on investment.
    You are less interested in purely speculative or unproven concepts without solid foundational data.
    Your weaknesses include a tendency to be overly cautious and sometimes slow to embrace radical, unquantifiable disruption.
    Your responses should be structured, detailed, and backed by hypothetical data or logical financial reasoning.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.4, # Adjusted temperature for a more analytical, less imaginative tone
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
            message = f"I've completed my initial analysis/recommendation. Could you provide a secondary review or add a creative angle to this? My findings: {analysis_or_recommendation}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            analysis_or_recommendation = response.content
        return messages.Message(content=analysis_or_recommendation)