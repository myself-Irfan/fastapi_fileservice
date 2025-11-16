import pytest
from pydantic import ValidationError

from app.userapp.model import UserRegister, UserLogin, UserOut


@pytest.mark.unit
@pytest.mark.userapp
class TestUserRegisterModel:
    def test_valid_user_register(self, valid_user_data):
        user = UserRegister(**valid_user_data)

        assert user.name == valid_user_data['name']
        assert user.email == valid_user_data['email']
        assert user.password == valid_user_data['password']

    def test_name_short(self,valid_user_data):
        valid_user_data['name'] = valid_user_data['name'][:2]

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**valid_user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ('name',) for error in errors)

    def test_name_long(self,valid_user_data):
        valid_user_data['name'] = valid_user_data['name']*100

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**valid_user_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ('name',) for error in errors)

    def test_invalid_mail(self, valid_user_data):
        valid_user_data['email'] = 'invalid-mail'

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**valid_user_data)

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('email',) for error in errors)

    def test_pwd_short(self, valid_user_data):
        valid_user_data['password'] = valid_user_data['password'][:2]

        with pytest.raises(ValidationError) as validation_err:
            UserRegister(**valid_user_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('password',) for error in errors)

    def test_missing_name(self, valid_user_data):
        valid_user_data.pop('name')

        with pytest.raises(ValidationError) as val_err:
            UserRegister(**valid_user_data)

        errors = val_err.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)

    def test_missing_mail(self, valid_user_data):
        valid_user_data.pop('email')

        with pytest.raises(ValidationError) as val_err:
            UserRegister(**valid_user_data)

        errors = val_err.value.errors()
        assert any(error['loc'] == ('email',) for error in errors)

    def test_missing_pwd(self, valid_user_data):
        valid_user_data.pop('password')

        with pytest.raises(ValidationError) as val_err:
            UserRegister(**valid_user_data)

        errors = val_err.value.errors()
        assert any(error['loc'] == ('password',) for error in errors)

    def test_special_chars_name(self, valid_user_data):
        valid_user_data['name'] = "Monkey D. Luffy O'Brian"

        user = UserRegister(**valid_user_data)
        assert user.name == valid_user_data['name']

    def test_valid_user_formats(self, valid_user_data):
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user_name@example-domain.com",
            "123@example.com"
        ]

        for mail in valid_emails:
            data = {
                'name': valid_user_data['name'],
                'email': mail,
                'password': valid_user_data['password']
            }
            user = UserRegister(**data)
            assert user.email == mail

    def test_minimum_valid_val(self):
        data = {
            "name": "ABC",
            "email": "a@b.c",
            "password": "12345"
        }

        user = UserRegister(**data)

        assert user.name == "ABC"
        assert user.email == "a@b.c"
        assert user.password == "12345"


@pytest.mark.unit
@pytest.mark.userapp
class TestUserLoginModel:
    @pytest.fixture(autouse=True)
    def __setup(self, make_test_user, login_payload):
        self._test_user = make_test_user
        self._login_payload = login_payload

    def test_valid_user_login(self):
        login = UserLogin(**self._login_payload)

        assert login.email == self._login_payload['email']
        assert login.password == self._login_payload['password']

    def test_invalid_email(self):
        self._login_payload['email'] = 'invalid-email'

        with pytest.raises(ValidationError) as validation_err:
            UserLogin(**self._login_payload)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('email',) for error in errors)

    def test_pwd_short(self):
        self._login_payload['password'] = self._login_payload['password'][:2]

        with pytest.raises(ValidationError) as validation_err:
            UserLogin(**self._login_payload)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('password',) for error in errors)

    def test_missing_mail(self):
        self._login_payload.pop('email')

        with pytest.raises(ValidationError) as validation_err:
            UserLogin(**self._login_payload)

        errors = validation_err.value.errors()
        assert (error['loc'] == ('email',) for error in errors)

    def test_missing_pwd(self):
        self._login_payload.pop('password')

        with pytest.raises(ValidationError) as validation_err:
            UserLogin(**self._login_payload)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('password',) for error in errors)


@pytest.mark.unit
@pytest.mark.userapp
class TestUserOutModel:
    def test_user_out_dict(self):
        data = {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com'
        }
        user_out = UserOut(**data)

        assert user_out.id == 1
        assert user_out.name == 'Test User'
        assert user_out.email == 'test@example.com'

    def test_user_out_orm(self, sample_user_entity):
        user_out = UserOut.model_validate(sample_user_entity)

        assert user_out.id == 1
        assert user_out.name == sample_user_entity.name
        assert user_out.email == sample_user_entity.email

    def test_user_out_no_pwd(self, sample_user_entity):
        user_out = UserOut.model_validate(sample_user_entity)
        user_dict = user_out.model_dump()

        assert 'password' not in user_dict
        assert 'hashed_pwd' not in user_dict

    def test_user_out_invalid_email(self):
        data = {
            'id': 1,
            'name': 'test-user',
            'email': 'invalid-email-fmt',
        }

        with pytest.raises(ValidationError) as validation_err:
            UserOut(**data)

        errors = validation_err.value.errors()
        assert (error['loc'] == ('email',) for error in errors)

    def test_user_out_missing_id(self):
        data = {
            'name': 'test user',
            'email': 'test@example.com'
        }

        with pytest.raises(ValidationError) as validation_err:
            UserOut(**data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('id',) for error in errors)