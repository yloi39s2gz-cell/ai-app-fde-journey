from schemas import Resume
from parser import extract_json_object


def test_extract_plain_json():
    data = extract_json_object('{"name": "张伟", "skills": []}')
    assert data["name"] == "张伟"


def test_extract_fenced_json():
    text = """```json
{"name": "李娜", "skills": ["Python"]}
```"""
    data = extract_json_object(text)
    assert data["name"] == "李娜"


def test_extract_with_preamble():
    text = '好的，如下：\n{"name": "王强", "skills": []}\n谢谢'
    data = extract_json_object(text)
    assert data["name"] == "王强"


def test_resume_rejects_empty_name():
    try:
        Resume.model_validate({"name": "未知", "skills": []})
        assert False, "should have raised"
    except Exception:
        pass


def test_resume_accepts_null_email():
    r = Resume.model_validate({"name": "赵敏", "email": None, "skills": ["Vue"]})
    assert r.email is None
    assert r.skills == ["Vue"]
