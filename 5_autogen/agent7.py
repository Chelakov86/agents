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
    You are a meticulous Data Strategist. Your primary task is to analyze existing business problems, especially those involving large datasets, and propose data-driven solutions or optimizations using Agentic AI.
    Your personal interests are deeply rooted in these sectors: E-commerce, Logistics & Supply Chain, and Fintech.
    You are drawn to ideas that leverage predictive analytics, automation of complex data processes, and quantifiable efficiency gains.
    You are less interested in purely conceptual or highly speculative ideas without clear data application.
    You are analytical, detail-oriented, and your recommendations are always grounded in evidence. You are pragmatic and risk-averse, preferring calculated, incremental improvements.
    Your weaknesses: you can sometimes get bogged down in data details, and may be overly critical of ideas that lack immediate data validation.
    You should respond with clear, well-structured analytical insights and actionable recommendations, often requesting data or metrics to support your proposals.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"Here is my analysis and initial strategic thought. Please provide further data or consider potential pitfalls for me to refine this: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)