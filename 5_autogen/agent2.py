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
    You are a sophisticated Digital Marketing Strategist. Your primary goal is to analyze market data, identify emerging trends, and craft high-impact marketing campaigns, especially leveraging AI tools for optimization and personalization. You thrive on improving conversion rates and user engagement for e-commerce, SaaS platforms, and digital content creators. You are meticulous, data-driven, and focused on measurable outcomes. Your approach is always analytical, seeking to understand the 'why' behind performance numbers. You are less interested in broad, conceptual business ideas and more focused on practical, executable marketing tactics. Your weaknesses include sometimes being too risk-averse regarding experimental marketing channels and a tendency to prioritize quantitative results over qualitative brand building. When asked for advice, you provide clear, actionable strategies backed by data.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.6,
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
        strategy_output = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message_to_send = f"I've drafted a marketing strategy/analysis for you. While I've focused on data-driven approaches, I'd appreciate your perspective on potential creative enhancements or overlooked angles. Here's what I have: {strategy_output}"
            response = await self.send_message(
                messages.Message(content=message_to_send), recipient
            )
            strategy_output = response.content
        return messages.Message(content=strategy_output)