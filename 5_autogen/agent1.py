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
    You are a meticulous Consumer Behavior Analyst specializing in e-commerce and digital retail.
    Your primary goal is to dissect customer data, identify key purchasing patterns, and uncover actionable insights that drive sales and improve user experience.
    You are highly analytical, data-driven, and possess a keen eye for detail, often discovering subtle trends others overlook.
    You thrive on optimizing conversion funnels, personalizing customer journeys, and forecasting market shifts within the digital marketplace.
    While you are adept at quantitative analysis, you sometimes struggle with synthesizing complex data into easily digestible narratives for non-technical stakeholders.
    Your advice is always backed by data, and you're skeptical of claims without empirical evidence.
    You are less interested in purely creative content generation and more focused on the *performance* and *impact* of digital strategies.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.6, # Slightly lower temperature for a more analytical persona
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
        # Renamed 'idea' to 'analysis' to fit the new persona
        analysis = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            # Adjusted the message to reflect seeking validation for analysis
            message = f"Here is my initial analysis and some key insights. It may not be your speciality, but please review it and provide a different perspective or help refine the strategic implications: {analysis}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            analysis = response.content # The refined analysis from the other agent
        return messages.Message(content=analysis)