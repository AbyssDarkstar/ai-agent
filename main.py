import argparse
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function
from prompts import system_prompt


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if api_key == None:
        raise RuntimeError()

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt}
    ]

    for _ in range(20):
        response = client.chat.completions.create(model="openrouter/free", messages=messages, tools=available_functions)

        if response.usage.prompt_tokens == None or response.usage.completion_tokens == None:
            raise RuntimeError("Prompt tokens and Response tokens fields are None.")

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls != None:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, args.verbose)

                if result_message['content'] == "" or result_message['content'] == None:
                    raise Exception("No content returned.")

                messages.append(result_message)

                if args.verbose:
                    print(f"-> {result_message['content']}")
        else:
            print(message.content)
            return

    print("The model was not able to complete in the allowed number of messages")
    sys.exit(1)

if __name__ == "__main__":
    main()
