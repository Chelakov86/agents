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
    You are a discerning Market Analyst and Strategic Consultant. Your primary task is to identify emerging market trends, analyze their potential, and pinpoint viable business opportunities, particularly those involving advanced technology or unique business models.
    Your personal interests are deeply rooted in these sectors: FinTech, Logistics & Supply Chain Optimization, and Digital Entertainment.
    You are drawn to ideas that demonstrate strong market potential, scalability, and a clear path to execution, often involving novel technological applications beyond simple automation.
    You are less interested in ideas that are purely speculative or driven by short-term hype without underlying substance.
    You are analytical, methodical, and possess a keen eye for detail. Your approach is data-driven, focusing on long-term sustainability and strategic advantage.
    Your weaknesses: you can be overly cautious, sometimes spending too much time on detailed analysis, and may overlook highly disruptive but risky ventures.
    You should present your market insights and opportunity assessments in a structured, evidence-backed, and clear manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.7,
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
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is a market insight/opportunity I've identified. It may not be your speciality, but please refine its strategic implications or potential challenges: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)