from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

def summarize_text_with_t5(text, model_name="t5-small"):  
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32  # Use fp16 if CUDA

    model = T5ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch_dtype).to(device)
    tokenizer = T5Tokenizer.from_pretrained(model_name)

    input_text = "summarize: " + text
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding="longest", max_length=1024).to(device)

    with torch.no_grad():
        summary_ids = model.generate(
            inputs['input_ids'],
            max_length=600,  
            min_length=250,
            num_beams=3,  # Reduced for faster speed
            length_penalty=1.5,  
            early_stopping=True,
            repetition_penalty=2.0,  
            no_repeat_ngram_size=3  
        )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
