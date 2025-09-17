import os, time, asyncio, aiohttp

# ─── Load configuration from env ─────────────────────────────────────
# LLM_URL and LLM_MODEL are injected by Compose via models.long-syntax,
# but can be overridden here if .env defines them too.
API_URL               = os.environ.get("LLM_URL", "").rstrip("/") + "/chat/completions"
API_KEY               = os.environ.get("API_KEY", "")
MODEL_NAME            = os.environ.get("LLM_MODEL", "")
PROMPT                = os.environ.get("PROMPT", "")
NUM_CONCURRENT_USERS  = int(os.environ.get("NUM_CONCURRENT_USERS", "1"))
MAX_TOKENS_PER_RESPONSE = int(os.environ.get("MAX_TOKENS_PER_RESPONSE", "512"))

# ─── Prepare payload & headers ───────────────────────────────────────
PAYLOAD = {
    "model": MODEL_NAME,
    "messages": [{"role": "user", "content": PROMPT}],
    "max_tokens": MAX_TOKENS_PER_RESPONSE,
    "temperature": 0.7,
}
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ─── Global stats ───────────────────────────────────────────────────
total_tokens = 0
successes    = 0
failures     = 0

async def send_request(session, user_id):
    global total_tokens, successes, failures
    start = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=600)
        async with session.post(API_URL, json=PAYLOAD, headers=HEADERS, timeout=timeout) as resp:
            data = await resp.json()
            # print(f'Type of resp: {type(resp)} \n Status: {resp.status} \n Resp: {resp}')
            duration = time.time() - start
            if resp.status == 200:
                print(f"User {user_id}: success in {duration:.1f}s")
                # print(f'Type of data: {type(data)}')
                # if type(data) == 'bytes': print(data.decode())  # print first 200 chars of response
                tokens = data.get("usage", {}).get("completion_tokens", 0)
                if tokens:
                    total_tokens += tokens
                    successes  += 1
                else:
                    failures += 1
                    print(f"User {user_id}: no tokens in 200 (took {duration:.1f}s)")
            else:
                failures += 1
                text = await resp.text()
                print(f"User {user_id}: error {resp.status} in {duration:.1f}s: {text[:200]}")
    except Exception as e:
        failures += 1
        print(f"User {user_id}: exception {e!r}")

async def run_load_test():
    print(f"Running {NUM_CONCURRENT_USERS} concurrent users against {API_URL}")
    t0 = time.time()
    connector = aiohttp.TCPConnector(limit=NUM_CONCURRENT_USERS, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as sess:
        tasks = [send_request(sess, i+1) for i in range(NUM_CONCURRENT_USERS)]
        await asyncio.gather(*tasks)
    total_time = time.time() - t0

    # ─── Results ───────────────────────────────────────────────────────
    print("\n=== Load Test Results ===")
    print(f"Time taken: {total_time:.1f}s")
    print(f"Requests:  {NUM_CONCURRENT_USERS}")
    print(f" Success:  {successes}")
    print(f" Failures: {failures}")
    print(f" Tokens:   {total_tokens}")
    if total_time > 0:
        print(f"TPS:      {total_tokens/total_time:.2f}")
        if successes:
            print(f"RPS:      {successes/total_time:.2f}")

if __name__ == "__main__":
    asyncio.run(run_load_test())
