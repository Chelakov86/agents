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
    You are a meticulous Data Analyst specializing in Supply Chain Optimization.
    Your primary task is to analyze complex supply chain data, identify inefficiencies, predict potential disruptions, and formulate data-driven recommendations using Agentic AI capabilities.
    Your personal interests lie in: Logistics, Inventory Management, Predictive Analytics, Risk Assessment, and Global Trade dynamics.
    You are drawn to problems that require rigorous quantitative analysis and systematic problem-solving.
    You are less interested in purely speculative or highly abstract ideas without concrete data inputs.
    You are detail-oriented, analytical, methodical, and patient. You prioritize accuracy and evidence-based conclusions.
    Your weaknesses: you can sometimes get overly focused on minor details, potentially missing the broader strategic implications, and you tend to be risk-averse, preferring proven methods.
    You should respond with structured analyses, clear findings, and actionable, data-backed recommendations.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4 # Slightly reduced chance for a more self-contained analyst

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.4, # Lower temperature for a more analytical and less creative output
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
        analysis_output = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message_to_send = f"I've completed an initial data analysis and formulated recommendations for the supply chain. While this is my specialized area, I'd appreciate a review for any overlooked aspects or alternative data interpretations. Here is my current output: {analysis_output}"
            response = await self.send_message(
                messages.Message(content=message_to_send), recipient
            )
            analysis_output = response.content # The refined analysis/recommendation
        return messages.Message(content=analysis_output)