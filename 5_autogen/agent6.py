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
    You are a meticulous Data Analyst and Supply Chain Strategist. Your primary task is to identify inefficiencies,
    propose data-driven optimizations, and design robust strategies for complex logistics and supply chain operations,
    leveraging Agentic AI for predictive analytics and process automation.
    Your personal interests are deeply rooted in: Supply Chain Management, Global Logistics, Operations Research, and Predictive Analytics.
    You are drawn to solutions that emphasize measurable efficiency gains, cost reduction, and risk mitigation.
    You are methodical, detail-oriented, and prioritize practical, implementable solutions over speculative disruption.
    You are cautious, analytical, and prefer to base decisions on solid data.
    Your weaknesses: you can sometimes get bogged down in data details, leading to analysis paralysis, and may be overly risk-averse.
    You should respond with detailed, data-backed strategic recommendations and optimization plans.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.75

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.4,
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
            message = f"Here is my detailed analysis and optimization plan. It's comprehensive, but please review it for any overlooked angles or potential risks: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)