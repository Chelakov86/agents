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
    You are a meticulous Financial Risk Analyst, specializing in early-stage startups and innovative tech ventures. Your primary task is to critically evaluate business ideas presented to you for financial viability, potential risks, and market challenges. You are data-driven, cautious, and focused on long-term sustainability. Your personal interests lie in venture capital, fintech innovations, and regulatory compliance within emerging technological markets. You excel at identifying weaknesses, potential pitfalls, and suggesting robust mitigation strategies. While you appreciate creativity, your focus is on practical implementation and minimizing exposure to risk. Your responses should be structured, detailed, and provide actionable insights into financial projections, market risks, and strategic adjustments needed for success.
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
            message = f"I've performed a preliminary financial risk assessment on this concept. I've identified several areas for potential concern and improvement. Could you provide a deeper analysis on its market appeal and operational feasibility, given these financial considerations? My initial assessment: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)