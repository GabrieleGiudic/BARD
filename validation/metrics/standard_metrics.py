import os
import json
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from tabulate import tabulate  # pip install tabulate

# NLTK resources
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

folder_path = r"C:\Users\g.giudici\Desktop\Phd\BARD\validation\output"

rouge = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
smooth = SmoothingFunction().method1

results = []

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bleu_scores, meteor_scores, rouge_scores = [], [], []
        
        for item in data:
            # Combine multiple lines into single string separated by periods
            ref_text = '. '.join([line.strip() for line in item["ground_truth"].split("\n") if line.strip()])
            pred_text = item["prediction"].strip()

            # Tokenize for BLEU and METEOR
            ref_tokens = [ref_text.split()]  # list of token lists
            pred_tokens = pred_text.split()

            # BLEU
            bleu_scores.append(sentence_bleu(ref_tokens, pred_tokens, smoothing_function=smooth))
            # METEOR
            meteor_scores.append(meteor_score(ref_tokens, pred_tokens))
            # ROUGE-L
            rouge_l = rouge.score(ref_text, pred_text)['rougeL'].fmeasure
            rouge_scores.append(rouge_l)

        # Average metrics per file
        avg_bleu = sum(bleu_scores)/len(bleu_scores) if bleu_scores else 0
        avg_meteor = sum(meteor_scores)/len(meteor_scores) if meteor_scores else 0
        avg_rouge = sum(rouge_scores)/len(rouge_scores) if rouge_scores else 0

        results.append([filename, round(avg_bleu, 4), round(avg_meteor, 4), round(avg_rouge, 4)])

# Print table
headers = ["File", "Average BLEU", "Average METEOR", "Average ROUGE-L"]
print(tabulate(results, headers=headers, tablefmt="grid"))
