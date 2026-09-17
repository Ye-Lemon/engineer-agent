from schemas.user import UserInfo

class Agent:
    def __init__(self,task_id,userinfo:UserInfo,*,llm_name):
        self.task_id = task_id
        self.userinfo = userinfo
        self.llm_name = llm_name

    def run_llm(self):
        """Return a deterministic fallback response when no LLM is configured."""
        return {
            "task_id": self.task_id,
            "model": self.llm_name,
            "content": "LLM provider is not configured; task queued for processing.",
        }

