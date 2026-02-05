import traceback
print('Python executable:', __import__('sys').executable)
try:
    from transformers import pipeline
    print('Transformers imported')
    try:
        print('Attempting zero-shot pipeline...')
        z = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
        print('Zero-shot loaded OK')
    except Exception as e:
        print('Zero-shot failed:')
        traceback.print_exc()
    try:
        print('Attempting Flan-T5 tokenizer/model...')
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tok = AutoTokenizer.from_pretrained('google/flan-t5-small')
        mod = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')
        print('Flan loaded OK')
    except Exception as e:
        print('Flan failed:')
        traceback.print_exc()
except Exception as e:
    print('Transformers import failed:')
    traceback.print_exc()
