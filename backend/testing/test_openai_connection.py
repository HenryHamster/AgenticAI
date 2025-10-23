# test_openai_connection.py
import sys
from openai import OpenAI

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_openai_connection.py <OPENAI_API_KEY>")
        sys.exit(1)

    api_key = sys.argv[1]
    client = OpenAI(api_key=api_key)

    print("Sending test request to OpenAI API...")

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",   # Try nano first; fallback to mini if needed
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=8,
            temperature=0,
        )
        print("\n✅ API call successful!")
        print("Response:", resp.choices[0].message.content)

    except Exception as e:
        print("\n❌ API call failed:")
        print(e)

if __name__ == "__main__":
    main()
