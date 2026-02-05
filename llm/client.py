import os
import json
from typing import Dict, Any
from openai import OpenAI


class LLMClient:
    """Wrapper for Nebius OpenAI-compatible API"""

    def __init__(self):
        api_key = os.environ.get("NEBIUS_API_KEY")
        if not api_key:
            raise EnvironmentError("NEBIUS_API_KEY environment variable is not set")

        self.client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1",
            api_key=api_key
        )

        # ✅ Correct Nebius OSS model
        self.model = "openai/gpt-oss-20b"

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a text response from the LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # ✅ HARD GUARD
            if not response or not response.choices:
                raise Exception("Empty response from LLM")

            content = response.choices[0].message.content

            if not content or not isinstance(content, str):
                raise Exception("LLM returned empty or invalid content")

            return content

        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate a STRICT JSON response from the LLM
        """

        json_system_prompt = f"""{system_prompt}

CRITICAL INSTRUCTIONS:
- Respond ONLY with valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include code blocks
"""

        response_text = self.generate(
            system_prompt=json_system_prompt,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # ✅ HARD GUARD AGAINST None / EMPTY
        if not response_text or not isinstance(response_text, str):
            raise Exception("LLM returned empty or invalid response")

        response_text = response_text.strip()

        # ✅ Remove markdown if model ignores instructions
        if response_text.startswith("```"):
            parts = response_text.split("```")
            if len(parts) >= 2:
                response_text = parts[1].strip()

        try:
            return json.loads(response_text)

        except json.JSONDecodeError as e:
            raise Exception(
                "Failed to parse JSON from LLM response\n"
                f"Error: {str(e)}\n"
                f"Raw response:\n{response_text}"
            )
