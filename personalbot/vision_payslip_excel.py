from openai import OpenAI
import os
import base64
import json
import sys
import requests
import pandas as pd
from decouple import config
OPENAI_API_KEY = config('OPENAI_API')
client = OpenAI(api_key=OPENAI_API_KEY)

file_name = 'daily_expenses.xlsx'

# Check if the file exists
if os.path.exists(file_name):
    # Load existing data
    df = pd.read_excel(file_name)
else:
    # Create a new DataFrame if the file does not exist
    df = pd.DataFrame(columns=['Date', 'Expense'])


Invoice_placement = {'''
                - The bank name or bank logo 
                - The text โอนเงินสำเร็จ / รายการสำเร็จ or Transaction Successful
                - The date and time of the transaction
                - The Name of sender
                - The Bank name of sender and the sender account number partially masked
                - The Name of receiver
                - The Bank name of receive and the receiver account number partially masked
                - Reference number of the transaction 
                - The amount of the transaction usually in Thai Baht บาท (sometimes in the middle of the image)
                - QR code of the invoice (usually in the bottom right of the image)
                '''
}

thai_months = {
    "มกราคม": "ม.ค.",
    "กุมภาพันธ์": "ก.พ.",
    "มีนาคม": "มี.ค.",
    "เมษายน": "เม.ย.",
    "พฤษภาคม": "พ.ค.",
    "มิถุนายน": "มิ.ย.",
    "กรกฎาคม": "ก.ค.",
    "สิงหาคม": "ส.ค.",
    "กันยายน": "ก.ย.",
    "ตุลาคม": "ต.ค.",
    "พฤศจิกายน": "พ.ย.",
    "ธันวาคม": "ธ.ค."
}

function_schema = [
    {
        "name":"extract_date_expense",
        "description": "Extract date and amount of money from the transaction",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date of Transaction"},
                "expense" : {"type": "number", "description": "Amount of money THB"}
            },
            "requried": ["date", "expense"]
        }
    }
]


def add_expense(date, expense):
    global df 
    new_expense = pd.DataFrame({'Date': [date], 'Expense': [expense]})
    df = pd.concat([df, new_expense], ignore_index=True)
    df.to_excel(file_name, index=False)


def get_daily_expenses():
    global df
    if df.empty:
        daily_expense_str = "ไม่มีบันทึกครับ"
    daily_expense = df.groupby('Date')['Expense'].sum()
    daily_expense_df = daily_expense.reset_index()
    daily_expense_df.columns = ['Date', 'Expense']
    daily_expense_str = daily_expense_df.to_string(index=False, header=True, justify='right')
    return daily_expense_str

def get_monthly_expenses():
    global df
    if df.empty:
        monthly_expense_str = "ไม่มีบันทึกครับ"
    monthly_expense = df.groupby(pd.to_datetime(df['Date'], dayfirst=True).dt.to_period('M'))['Expense'].sum()
    monthly_expense_df = monthly_expense.reset_index()
    monthly_expense_df.columns = ['Month', 'Total Expense']
    monthly_expense_str = monthly_expense_df.to_string(index=False, header=True, justify='right')

    return monthly_expense_str


def get_text_from_payslip(image_path=None, image_url=None):
    if image_path:
        with open(image_path, "rb") as image:
            base64_image = base64.b64encode(image.read()).decode("utf-8")   

    elif image_url:
        image = requests.get(image_url)
        base64_image = base64.b64encode(image.content).decode("utf-8")
    else:
        raise ValueError("Either image_path or image_url must be provided.")      

    response1 = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    response_format={"type": "json_object"},
    messages=[
            {
                "role": "system",
                "content": """You are a Thai accountant.A user sends you an image of a Thai Banking Slip or invoice and you tell them the information in it.
                YOU MUST CONVERT THE MONTH IN THAI OR ENGLISH LANGUAGE INTO ORIDINAL MONTH EG: JANUARY = 01, DECEMBER = 12
                YOU MUST CONVERT THE BUDDHIST YEAR INTO CHRISTIAN YEAR EG: 2567 INTO 2024, 2566 INTO 2023 (543 DIFFERENCES)
                The Invoice follows the placement rules from the top to bottom of the image:
                {invoice_placement}     
                 Use the following JSON format:
{                           
    "Date": "Date/Month/Year (if the date is in Thai Language it is usaully the shortform of how Thai people write in this format {thai_months} and convert the months into number of the month eg. January is 01
    "Expenses" :"The Amount of the Transaction in the format of Amount THB",
}"""
            },
            {
                "role": "user",                     
                "content": [
                    {
                        "type": "text",
                        "text": "What is the date and amount of this transaction"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            },
        ],
    )

    response_message = response1.choices[0].message  # select the first choice of the llm answers
    # content = response_message
    content_json = response_message.content  # .content (from openai lib) access the content of the message
    
    response2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": str(content_json)}],
        functions=function_schema,
        function_call="auto"
    )
    # output formatted examples
    # ChatCompletionMessage(content=None, role='assistant', function_call=
    # FunctionCall(arguments='{"date":"13/07/2024","expense":75}', name='extract_date_expense'), tool_calls=None, refusal=None)
    
    arguments = response2.choices[0].message.function_call.arguments
    data = json.loads(arguments)

    # Map to variables
    date = data['date']
    expense = data['expense']
    add_expense(date,expense)
    return expense


if __name__ == "__main__":
    image_path = './slip/slip9.png'
    result = get_text_from_payslip(image_path)
