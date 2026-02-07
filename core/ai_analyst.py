import google.generativeai as genai
import os

class GeminiAnalyst:
    def __init__(self, api_key=None, model_name='gemini-1.5-pro'):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    def list_models(self):
        """List available models for the configured API key."""
        if not self.api_key:
            return ["API Key not set"]
        try:
            return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except Exception as e:
            return [f"Error listing models: {str(e)}"]

    def analyze_market(self, context_data):
        """
        Generate market commentary based on structured context.
        context_data: dict containing liquidity, sentiment, and trend metrics.
        """
        if not self.model:
            return "Please configure Gemini API Key in the sidebar to enable AI analysis."

        prompt = f"""
        You are a professional macro-quant trader. Analyze the following China A-share market data and provide a brief evaluation.
        
        **Objective**: Determine if the market is safe for trading (avoid "catching falling knives") based on the following framework:
        
        1. **Liquidity (Funding)**: 
           - Margin Balance: {context_data.get('margin_balance', 'N/A')}
           - Money Supply (M1-M2 Scissors): {context_data.get('m1_m2_scissors', 'N/A')}
           - *Interpretation*: Rising margin balance = Retail entering (Overheat risk). Widening negative scissors = Liquidity Trap.
           
        2. **Sentiment (Panic)**:
           - NHR (New High/Low Ratio): {context_data.get('nhr', 'N/A')}
           - Panic Index (Decline Count Ratio): {context_data.get('panic_index', 'N/A')}
           - *Interpretation*: Panic Index > 80% = Extreme Fear (Short-term bounce likely). NHR Low = Bearish.
           
        3. **Trend (Technical)**:
           - Index vs EMA200: {context_data.get('trend_status', 'N/A')}
           - *Interpretation*: Below EMA200 = Bear Market (Defensive/Short). Above = Bull Market (Long).

        **Output Format**:
        - **Verdict**: [Safe to Trade / Wait & See / Catch Knife Opportunity]
        - **Analysis**: 2-3 sentences explaining the verdict using the data above.
        - **Risk Warning**: 1 sentence on the biggest current risk.
        
        Keep it concise and professional.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Analysis failed: {str(e)}"
