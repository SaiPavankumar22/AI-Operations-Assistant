from typing import Dict, Any


class VerifierAgent:
    def verify_results(
        self,
        original_task: str,
        execution_results: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        if execution_results.get("errors"):
            return self._incomplete(
                reason="Execution errors occurred",
                execution_results=execution_results,
                confidence="low"
            )


        final_data = execution_results.get("final_data")
        if not final_data:
            return self._incomplete(
                reason="No data returned from tools",
                execution_results=execution_results,
                confidence="low"
            )


        final_answer = self._format_final_answer(original_task, final_data)

        return {
            "is_complete": True,
            "confidence": "high",
            "final_answer": final_answer,
            "issues_found": [],
            "missing_data": [],
            "suggestions": []
        }

    def _format_final_answer(self, task: str, data: Any) -> str:


        if isinstance(data, dict) and "articles" in data:
            articles = data["articles"]

            if not articles:
                return "No relevant news articles were found."

            lines = [
                "Here are the most recent Tesla-related news articles from the last month:\n"
            ]

            for i, article in enumerate(articles, start=1):
                title = article.get("title", "No title")
                source = article.get("source", {}).get("name", "Unknown source")
                published = article.get("publishedAt", "Unknown date")
                url = article.get("url", "")

                lines.append(
                    f"{i}. {title}\n"
                    f"   Source: {source}\n"
                    f"   Published: {published}\n"
                    f"   Link: {url}\n"
                )

            return "\n".join(lines)

        # WEATHER RESULTS
        if isinstance(data, dict) and "temperature" in data:
            return (
                f"Current Weather Report:\n"
                f"Temperature: {data.get('temperature')} {data.get('units')}\n"
                f"Condition: {data.get('description')}\n"
                f"Humidity: {data.get('humidity')}%\n"
                f"Wind Speed: {data.get('wind_speed')} m/s"
            )

        # FALLBACK
        return str(data)

    def _incomplete(
        self,
        reason: str,
        execution_results: Dict[str, Any],
        confidence: str
    ) -> Dict[str, Any]:

        return {
            "is_complete": False,
            "confidence": confidence,
            "final_answer": f"Unable to fully complete the task: {reason}.",
            "issues_found": [reason],
            "missing_data": [],
            "suggestions": [],
            "raw_results": execution_results
        }

    def format_output(self, verification_result: Dict[str, Any]) -> str:
        output = []
        output.append("=" * 60)
        output.append("AI OPERATIONS ASSISTANT - RESULTS")
        output.append("=" * 60)

        status = "✓ COMPLETE" if verification_result.get("is_complete") else "⚠ INCOMPLETE"
        output.append(f"\nStatus: {status}")
        output.append(f"Confidence: {verification_result.get('confidence', '').upper()}")

        if verification_result.get("issues_found"):
            output.append("\n⚠ Issues Found:")
            for issue in verification_result["issues_found"]:
                output.append(f"  - {issue}")

        output.append("\n" + "=" * 60)
        output.append("ANSWER:")
        output.append("=" * 60)
        output.append(verification_result.get("final_answer", "No answer available"))

        output.append("\n" + "=" * 60)
        return "\n".join(output)
