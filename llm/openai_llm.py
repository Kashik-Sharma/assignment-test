# import openai
#
# # Set your Azure OpenAI API key and endpoint
# api_key = "b3ccd66ef7c34ed1994739bb3d30bcbe"
# api_endpoint = "https://productcreator.openai.azure.com/"
#
# # # Set the model and configuration parameters
# # model = "gpt-4o-2"  # You can also use "gpt-4" or another model
# # max_tokens = 8192
# # temperature = 1
# # top_p = 0.95
# #
# # # Function to call Azure OpenAI API for text generation
# # def generate(input_text):
# #     """
# #     Generate a response from Azure OpenAI GPT model (e.g., GPT-3.5 or GPT-4).
# #
# #     :param input_text: The input prompt to send to the model
# #     :return: The generated text from the model
# #     """
# #     # Set up the API key and endpoint
# #     openai.api_key = api_key
# #     openai.api_base = api_endpoint
# #
# #     try:
# #         # Make the API call to Azure OpenAI's completion model (e.g., GPT-3.5 or GPT-4)
# #         response = openai.Completion.create(
# #             model=model,
# #             prompt=input_text,
# #             max_tokens=max_tokens,
# #             temperature=temperature,
# #             top_p=top_p,
# #             n=1,  # Number of completions to generate
# #             stop=None,  # You can specify stop sequences if needed
# #         )
# #
# #         # Extract and return the response text
# #         response_text = response.choices[0].text.strip()  # Get the generated text
# #         print(response_text)  # Print the response for debugging
# #         return response_text
# #
# #     except Exception as e:
# #         print(f"Error generating response: {e}")
# #         return None
#
#
# # import getpass
# # import os
# #
# # if not os.environ.get("OPENAI_API_KEY"):
# #     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
#
#
# from langchain_openai import ChatOpenAI
#
# llm = ChatOpenAI(
#     model="gpt-4o-2",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     api_key=api_key,  # if you prefer to pass api key in directly instaed of using env vars
#     base_url=api_endpoint
# )
#
# output = llm.invoke("How can you help me?")
# print(output)





from langchain_openai import ChatOpenAI

# Set your API key and endpoint (ensure these are correct)
api_key = "your-azure-api-key"
api_endpoint = "https://your-resource-name.openai.azure.com/"

# Use a valid model, for example, "gpt-4" or "gpt-3.5-turbo"
llm = ChatOpenAI(
    model="gpt-4",  # Make sure this is the correct model available in your Azure resource
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key,  # You can pass the API key directly if not using environment variables
    base_url=api_endpoint
)

# Test the LLM with a query
output = llm.invoke("How can you help me?")
print(output)
