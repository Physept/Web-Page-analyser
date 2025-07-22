from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)

# Load Hugging Face QA model
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Store last scraped content
cached_content = ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    global cached_content
    data = request.get_json()
    url = data.get('url')

    cached_content = ""  # Reset previous content

    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        text = soup.get_text(separator=' ')
        lines = [line.strip() for line in text.splitlines()]
        clean_text = '\n'.join(line for line in lines if line)

        cached_content = clean_text
        preview = clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text

        return jsonify({
            'message': f'Content extracted from {url}',
            'content': preview
        })

    except Exception as e:
        return jsonify({
            'message': 'Failed to extract content.',
            'error': str(e)
        })

@app.route('/ask', methods=['POST'])
def ask():
    global cached_content
    data = request.get_json()
    question = data.get('question')

    print("Received question:", question)
    print("Cached content length:", len(cached_content))

    if not cached_content:
        return jsonify({'error': 'No content to search. Please analyze a webpage first.'})

    try:
        best_answer = ""
        best_score = 0.0

        # Chunk context into pieces of ~500 words
        words = cached_content.split()
        chunks = [' '.join(words[i:i + 500]) for i in range(0, len(words), 500)]

        for chunk in chunks:
            result = qa_pipeline({
                'question': question,
                'context': chunk
            })
            print("Chunk answer:", result['answer'], "| score:", result['score'])
            if result['score'] > best_score:
                best_score = result['score']
                best_answer = result['answer']

        if best_answer:
            return jsonify({'answer': best_answer})
        else:
            return jsonify({'answer': "Sorry, I couldn't find a relevant answer."})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
