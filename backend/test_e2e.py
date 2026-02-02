#!/usr/bin/env python3
"""End-to-end validation tests for Module 1."""

import os
import sys
import time
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

API_URL = "http://localhost:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Test credentials - use existing test user
TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "test123"


def print_result(test_name: str, passed: bool, details: str = ""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"       {details}")


def main():
    print("=" * 60)
    print("Module 1: End-to-End Validation Tests")
    print("=" * 60)
    print()

    # Check configuration
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("[SKIP] Supabase credentials not configured")
        print("       Add SUPABASE_URL and SUPABASE_ANON_KEY to .env")
        return 1

    # Initialize Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    # Test 1: Health check
    print("1. Backend Health Check")
    try:
        resp = requests.get(f"{API_URL}/health")
        print_result("Health endpoint", resp.status_code == 200, resp.json().get("status"))
    except Exception as e:
        print_result("Health endpoint", False, str(e))
        return 1

    # Test 2: Auth rejection without token
    print("\n2. Auth Middleware")
    resp = requests.get(f"{API_URL}/api/threads")
    print_result("Rejects unauthenticated requests", resp.status_code == 401)

    # Test 3: Sign in existing user
    print("\n3. User Sign In")
    try:
        auth_resp = supabase.auth.sign_in_with_password({"email": TEST_EMAIL, "password": TEST_PASSWORD})
        if auth_resp.user:
            print_result("Sign in user", True, f"User ID: {auth_resp.user.id[:8]}...")
            access_token = auth_resp.session.access_token if auth_resp.session else None
        else:
            print_result("Sign in user", False, "No user returned")
            return 1
    except Exception as e:
        print_result("Sign in user", False, str(e))
        return 1

    if not access_token:
        print("[SKIP] No access token - email confirmation may be required")
        print("       Disable 'Confirm email' in Supabase Auth settings for testing")
        return 1

    headers = {"Authorization": f"Bearer {access_token}"}

    # Test 4: Create thread
    print("\n4. Thread Management")
    resp = requests.post(f"{API_URL}/api/threads", json={"title": "Test Thread"}, headers=headers)
    if resp.status_code == 201:
        thread = resp.json()
        thread_id = thread["id"]
        print_result("Create thread", True, f"Thread ID: {thread_id[:8]}...")
    else:
        print_result("Create thread", False, resp.text)
        return 1

    # Test 5: List threads
    resp = requests.get(f"{API_URL}/api/threads", headers=headers)
    print_result("List threads", resp.status_code == 200 and len(resp.json()) > 0)

    # Test 6: Get single thread
    resp = requests.get(f"{API_URL}/api/threads/{thread_id}", headers=headers)
    print_result("Get thread", resp.status_code == 200)

    # Test 7: Get messages (empty)
    resp = requests.get(f"{API_URL}/api/threads/{thread_id}/messages", headers=headers)
    print_result("Get messages (empty)", resp.status_code == 200 and len(resp.json()) == 0)

    # Test 8: Chat with SSE streaming
    print("\n5. Chat & Streaming")
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[SKIP] OPENAI_API_KEY not configured - skipping chat test")
    else:
        try:
            resp = requests.post(
                f"{API_URL}/api/threads/{thread_id}/chat",
                json={"content": "Hello, say just 'Hi' back."},
                headers=headers,
                stream=True,
            )
            if resp.status_code == 200:
                content = ""
                for line in resp.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data:"):
                            content += decoded[5:].strip()
                print_result("SSE streaming chat", len(content) > 0, f"Response length: {len(content)} chars")
            else:
                print_result("SSE streaming chat", False, resp.text)
        except Exception as e:
            print_result("SSE streaming chat", False, str(e))

        # Test 9: Messages saved (wait a moment for async save to complete)
        time.sleep(1)
        resp = requests.get(f"{API_URL}/api/threads/{thread_id}/messages", headers=headers)
        messages = resp.json()
        has_both = len(messages) >= 2 and any(m["role"] == "user" for m in messages) and any(m["role"] == "assistant" for m in messages)
        print_result("Messages persisted", has_both, f"{len(messages)} messages")

    # Test 10: Delete thread
    print("\n6. Cleanup")
    resp = requests.delete(f"{API_URL}/api/threads/{thread_id}", headers=headers)
    print_result("Delete thread", resp.status_code == 204)

    # Test 11: RLS - create second user and try to access first user's data
    print("\n7. RLS Security")
    try:
        # Create another thread with first user
        resp = requests.post(f"{API_URL}/api/threads", json={"title": "Private Thread"}, headers=headers)
        private_thread_id = resp.json()["id"]

        # Sign up second user
        test_email_2 = f"test2_{int(time.time())}@example.com"
        auth_resp_2 = supabase.auth.sign_up({"email": test_email_2, "password": TEST_PASSWORD})
        if auth_resp_2.session:
            headers_2 = {"Authorization": f"Bearer {auth_resp_2.session.access_token}"}

            # Try to access first user's thread
            resp = requests.get(f"{API_URL}/api/threads/{private_thread_id}", headers=headers_2)
            print_result("RLS blocks cross-user access", resp.status_code == 404)

            # List threads should be empty for new user
            resp = requests.get(f"{API_URL}/api/threads", headers=headers_2)
            print_result("RLS isolates user data", resp.status_code == 200 and len(resp.json()) == 0)
        else:
            print("[SKIP] Could not create second test user")

        # Cleanup
        requests.delete(f"{API_URL}/api/threads/{private_thread_id}", headers=headers)
    except Exception as e:
        print_result("RLS security tests", False, str(e))

    print("\n" + "=" * 60)
    print("Validation Complete")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
