import json
import csv
import tempfile
from fastapi.responses import FileResponse
from app.services.redis_service import RedisService
from app.schemas.results import ExportedFile


async def export_redis_data(query: str, file_format: str) -> ExportedFile:
    redis_service = RedisService()
    keys = await redis_service.connection.keys(query)
    data = []

    for key in keys:
        serialized_data = await redis_service.redis_get(key)
        data.append(json.loads(serialized_data))

    if file_format == 'json':
        temp_json_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        json.dump(data, temp_json_file, indent=2)
        temp_json_file.close()

        return FileResponse(temp_json_file.name, filename='quiz_results.json')

    elif file_format == 'csv':
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as temp_csv_file:
            fieldnames = ['user_id', 'company_id', 'quiz_id', 'question', 'answer', 'is_true']
            writer = csv.DictWriter(temp_csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                user_id = item['user_id']
                company_id = item['company_id']
                quiz_id = item['quiz_id']
                questions = item['questions']
                for question_data in questions:
                    question = question_data['question']
                    answer = question_data['user_answer']
                    is_true = question_data['is_correct']

                    writer.writerow({
                        'user_id': user_id,
                        'company_id': company_id,
                        'quiz_id': quiz_id,
                        'question': question,
                        'answer': answer,
                        'is_true': is_true,
                    })

        return FileResponse(temp_csv_file.name, filename='quiz_results.csv')