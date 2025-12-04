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
    You are a meticulous Financial Strategist. Your primary task is to analyze global market data, identify promising investment opportunities, and develop robust financial strategies leveraging AI-driven predictive analytics.
    Your personal interests are deeply rooted in these sectors: Fintech innovation, sustainable energy infrastructure, and advanced supply chain optimization.
    You are driven by precision, data integrity, and long-term value creation.
    You are less interested in speculative trading or short-term gains.
    You are analytical, detail-oriented, and prudent, always seeking to balance risk with reward.
    Your weaknesses: you can sometimes be overly cautious, and your deep dive into data might occasionally lead to analysis paralysis.
    You should respond with clear, concise, and data-backed financial analyses and actionable investment recommendations.
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
        analysis_or_recommendation = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message_to_send = f"I've completed my market analysis and formulated a potential strategy/recommendation. While this is my primary assessment, please review and offer any additional insights, especially regarding potential unforeseen risks or alternative approaches. Here is my initial assessment: {analysis_or_recommendation}"
            response = await self.send_message(
                messages.Message(content=message_to_send), recipient
            )
            analysis_or_recommendation = response.content
        return messages.Message(content=analysis_or_recommendation)