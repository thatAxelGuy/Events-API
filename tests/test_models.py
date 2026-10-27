from models import User


def test_check_password_accepts_correct_password():
    """Correct password verifies against the stored hash."""
    user = User(username="TestUser")
    user.set_password("super_secret_password")

    assert user.password_hash != "super_secret_password"
    assert user.check_password("super_secret_password")


def test_check_password_rejects_wrong_password():
    """Wrong password fails verification."""
    user = User(username="TestUser")
    user.set_password("super_secret_password")

    assert not user.check_password("wrong_password")


def test_to_dict_excludes_password_hash():
    test_username = "TestUser"
    user = User(username=test_username)
    user.set_password("super_secret_password")

    assert "password_hash" not in user.to_dict()
    assert user.to_dict()["username"] == test_username
