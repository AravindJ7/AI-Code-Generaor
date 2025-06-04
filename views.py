from django.shortcuts import render
from datetime import datetime
from pymongo import MongoClient
from .code_engine import generate_code, format_code, analyze_code, execute_code

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["code_assistant"]
collection = db["generated_codes"]

def home(request):
    context = {}

    if request.method == "POST":
        action = request.POST.get("action")
        user_input = request.POST.get("user_input", "")
        prompt = request.POST.get("prompt", "")

        if action == "generate":
            code = generate_code(user_input)
            context['generated_code'] = code

        elif action == "execute":
            output = execute_code(user_input)
            context['execution_output'] = output

        elif action == "format":
            formatted = format_code(user_input)
            context['formatted_code'] = formatted

        elif action == "analyze":
            analysis = analyze_code(user_input)
            context['analysis'] = analysis
            # Simple rating based on presence of errors/warnings
            rating = 10
            if "error" in analysis.lower() or "fatal" in analysis.lower():
                rating -= 5
            if "warning" in analysis.lower():
                rating -= 2
            context['rating'] = max(rating, 1)

        elif action == "save":
            collection.insert_one({
                "prompt": prompt,
                "generated_code": user_input,
                "timestamp": datetime.now()
            })
            context['save_status'] = "Code saved to MongoDB."

    return render(request, 'assistant/index.html', context)

