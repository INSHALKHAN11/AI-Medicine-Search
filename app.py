from flask import Flask, render_template, request
from openai import OpenAI
import json
import os

app = Flask(__name__)

print("APP FILE:", __file__)
print("CURRENT DIR:", os.getcwd())
print("STATIC EXISTS:", os.path.exists("static"))
print("STYLE EXISTS:", os.path.exists("static/style.css"))    

client = OpenAI(
    api_key="sk-...o0AA"
)

# Load medicines database
with open('data/medicines.json') as f:
    medicines = json.load(f)

# Load export rules database
with open('data/export_rules.json') as f:
    export_rules = json.load(f)

def ai_summary(medicine):

    response = client.responses.create(
        model="gpt-5",
        input=f"""
        Explain the medicine {medicine}
        in simple language.
        Mention:
        - Uses
        - Benefits
        - Common precautions
        """
    )
    return response.output_text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():

    medicine_name = request.form['medicine']

    country = request.form['country']

    result = None

    for med in medicines:

        if (
            medicine_name.lower() in med["name"].lower()
            or
            medicine_name.lower() in med["generic"].lower()
        ):
            result = med
            break

    export_status = "Unknown"
    documents = []
    summary = ""

    if result:

        generic = result["generic"]

        summary = ai_summary(generic)

        if generic in export_rules[country]["medicines"]:

            export_status = "Eligible"

            documents = export_rules[country]["documents"]

        else:

            export_status = "Not Eligible"
            
    print("COUNTRY =", country)
    print("GENERIC =", generic if result else "None")
    print("STATUS =", export_status)
    print("DOCUMENTS =", documents)

    return render_template(
        'result.html',
        medicine=result,
        country=country,
        export_status=export_status,
        documents=documents,
        summary=summary,
        images=images
    )

if __name__ == "__main__":
    app.run(debug=True)
