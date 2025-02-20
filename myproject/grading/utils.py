import os
import re
import subprocess
import javalang
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Load CodeBERT Model
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

import javalang

def analyze_ast(code):
    try:
        tree = javalang.parse.parse(code)

        # Kategori elemen sintaks
        keywords = {"public", "class", "static", "void", "int", "System", "main", "String"}
        data_types = {"byte", "short", "int", "long", "float", "double", "char", "boolean", "String"}
        control_structures = {"if", "for", "while", "switch", "else"}
        operators = {":", "=", "+=", "%", "==", "<", ">", "+", "-", "*", "/"}
        delimiters = {"{", "}", "(", ")", "[", "]", ";"}
        exception_handling = {"try", "catch", "throw", "throws"}
        io_keywords = {"System.out.println", "System.in"}

        # Hasil analisis
        detected = {
            "classes": set(),
            "variables": set(),
            "data_types": set(),
            "parameters": set(),
            "keywords": set(),
            "control_structures": set(),
            "operators": set(),
            "delimiters": set(),
            "exceptions": set(),
            "io": set(),
            "arrays": set(),
            "methods": set(),
        }

        # Iterasi melalui AST untuk menemukan elemen sintaks
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                detected["classes"].add(node.name)
            elif isinstance(node, javalang.tree.MethodDeclaration):
                if node.name == "main":
                    detected["keywords"].add("main")
                detected["methods"].add(node.name)
                for param in node.parameters:
                    detected["parameters"].add(param.type.name)
            elif isinstance(node, javalang.tree.VariableDeclarator):
                detected["variables"].add(node.name)
            elif isinstance(node, javalang.tree.Type):
                detected["data_types"].add(node.name)
            elif isinstance(node, javalang.tree.MethodInvocation):
                detected["io"].add("System.out.println" if "System.out.println" in node.member else "")
                detected["methods"].add(node.member)
            elif isinstance(node, javalang.tree.IfStatement):
                detected["control_structures"].add("if")
            elif isinstance(node, javalang.tree.ForStatement):
                detected["control_structures"].add("for")
            elif isinstance(node, javalang.tree.WhileStatement):
                detected["control_structures"].add("while")
            elif isinstance(node, javalang.tree.ArrayInitializer):
                detected["arrays"].add("array")
            elif isinstance(node, javalang.tree.TryStatement):
                detected["exceptions"].add("try")
            elif isinstance(node, javalang.tree.CatchClause):
                detected["exceptions"].add("catch")
            elif isinstance(node, javalang.tree.ThrowStatement):
                detected["exceptions"].add("throw")

        # Parsing manual untuk mendeteksi operator dan delimiter
        for token in javalang.tokenizer.tokenize(code):
            if token.value in keywords:
                detected["keywords"].add(token.value)
            elif token.value in data_types:
                detected["data_types"].add(token.value)
            elif token.value in control_structures:
                detected["control_structures"].add(token.value)
            elif token.value in operators:
                detected["operators"].add(token.value)
            elif token.value in delimiters:
                detected["delimiters"].add(token.value)
            elif token.value in exception_handling:
                detected["exceptions"].add(token.value)
            elif token.value in io_keywords:
                detected["io"].add(token.value)

        # Konversi hasil ke bentuk dictionary dengan list
        return {key: sorted(list(value)) for key, value in detected.items()}

    except Exception as e:
        return {"error": f"Error dalam analisis AST: {e}"}

# Fungsi untuk memeriksa sintaks Java
def check_syntax(java_code, class_name):
    file_name = f"{class_name}.java"
    with open(file_name, 'w') as f:
        f.write(java_code)
    result = subprocess.run(['javac', file_name], capture_output=True, text=True)
    os.remove(file_name)

    return result.returncode == 0, result.stderr if result.returncode != 0 else "Sintaks benar"

# Fungsi untuk membersihkan kode Java
def clean_code(code):
    code = re.sub(r'//.*?|/\*.*?\*/', '', code, flags=re.DOTALL)  # Hapus komentar
    code = re.sub(r'\s+', ' ', code).strip()  # Hapus spasi berlebih
    return code

# Fungsi untuk membuat vektor embedding menggunakan CodeBERT
def bert_vectorize(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

# Fungsi untuk menghitung similarity menggunakan Cosine Similarity
def calculate_similarity(code1, code2):
    vec1 = bert_vectorize(code1)
    vec2 = bert_vectorize(code2)
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return round(similarity * 100, 2)  # Skala 0-100%
