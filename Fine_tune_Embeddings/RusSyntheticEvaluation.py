# После этого в файле generated_queries_and_excerpts.csv 
# и при выводе через print(df.head()) вы получите нормальный русский текст
#  внутри поля references, без юникод-эскейпов.

import json
import pandas as pd
from chunking_evaluation import SyntheticEvaluation

class RusSyntheticEvaluation(SyntheticEvaluation):
    """
    Наследник, который при сохранении вопросов
    сериализует поле `references` с ensure_ascii=False.
    """
    def _generate_corpus_questions(self, corpus_id, approx=False, n=5):
        # точно копируем весь код оригинального метода, 
        # но одну строку `json.dumps` меняем на ensure_ascii=False
        
        with open(corpus_id, 'r', encoding='utf-8') as file:
            corpus = file.read()

        i = 0
        while i < n:
            while True:
                try:
                    prev = self.synth_questions_df[
                        self.synth_questions_df['corpus_id'] == corpus_id
                    ]['question'].tolist()

                    if approx:
                        q, refs = self._extract_question_and_approx_references(corpus, 4000, prev)
                    else:
                        q, refs = self._extract_question_and_references(corpus, 4000, prev)

                    if len(refs) > 5:
                        raise ValueError("Слишком много ссылок")

                    # Вот она — нужная строка с ensure_ascii=False
                    references = [
                        {'content': text, 'start_index': s, 'end_index': e}
                        for (text, s, e) in refs
                    ]
                    new_q = {
                        'question': q,
                        'references': json.dumps(references, ensure_ascii=False),
                        'corpus_id': corpus_id
                    }

                    new_df = pd.DataFrame([new_q])
                    self.synth_questions_df = pd.concat(
                        [self.synth_questions_df, new_df],
                        ignore_index=True
                    )
                    self._save_questions_df()
                    break

                except (ValueError, json.JSONDecodeError) as e:
                    print("Ошибка:", e)
                    continue

            i += 1