from behave import given, when, then
import requests


BASE_URL = "http://app:8001"


@given('the user provides valid email and password')
def step_register_user(context):
   context.email = "dmd234567@gmail.com"
   context.password = "password"


@when('the user registers')
def step_register(context):
   response = requests.post(f"{BASE_URL}/register", json={
       "email": context.email,
       "password": context.password
   })
   context.response = response


@then('the user receives a verification email')
def step_verify_email(context):
   context.verification_code = "1234"


@then('the user confirms the email')
def step_verify_email(context):
    response = requests.post(f"{BASE_URL}/verify", json={
        "email": context.email,
        "code": context.verification_code
    })
    context.response = response

    assert context.response.status_code == 200


@given('the user has registered and verified email')
def step_login_user(context):
    context.email = "dmd234567@gmail.com"
    context.password = "password"
    context.wrong_password = "wrong_password"
    context.verification_code = "1234"


@when('the user attempts to log in with wrong password')
def step_login_failed(context):
   response = requests.post(f"{BASE_URL}/login", json={
       "email": context.email,
       "password": context.wrong_password
   })
   context.response = response


@then('the user should failed log in')
def step_login_failed(context):
   assert context.response.status_code == 400


@when('the user attempts to log in with correct password')
def step_login_success(context):
   response = requests.post(f"{BASE_URL}/login", json={
       "email": context.email,
       "password": context.password
   })
   context.response = response


@then('the user should successfully log in')
def step_login_success(context):
   assert context.response.status_code == 200


@given('the user has registered verified email and old password')
def step_provide_email_and_password(context):
    context.email = "dmd234567@gmail.com"
    context.old_password = "password"


@when('the user requests a password reset')
def step_request_password_reset(context):
   response = requests.post(f"{BASE_URL}/reset-password/request", json={
       "email": context.email,
       "old_password": context.old_password
   })
   context.response = response


@then('the user should receive a verification code via email')
def step_receive_verification_code(context):
    context.verification_code = "1234"


@then('the user confirms the verification code')
def step_receive_verification_code(context):
    assert context.verification_code == "1234"
    assert context.response.status_code == 200


@given('the user has registered verified email, new_password and verification code')
def step_provide_email_and_password(context):
    context.email = "dmd234567@gmail.com"
    context.new_password = "new_password"
    context.verification_code = "1234"


@when('the user confirms the password reset with the new password')
def step_confirm_password_reset(context):
   response = requests.post(f"{BASE_URL}/reset-password/confirm", json={
       "email": context.email,
       "new_password": context.new_password,
       "code": context.verification_code
   })
   context.response = response


@then('the user\'s password should be successfully changed')
def step_password_changed(context):
   assert context.response.status_code == 200


@given('the user provides email and password')
def step_provide_email_and_password(context):
    context.email = "dmd234567@gmail.com"
    context.password = "new_password"
    context.wrong_password = "wrong_password"


@when('the user wants to delete an account using incorrect data')
def step_delete_failed(context):
   response = requests.post(f"{BASE_URL}/delete", json={
       "email": context.email,
       "password": context.wrong_password
   })
   context.response = response


@then('an error should return stating that the data is incorrect')
def step_delete_failed(context):
   assert context.response.status_code == 400


@when('the user wants to delete an account using correct data')
def step_delete_success(context):
   response = requests.post(f"{BASE_URL}/delete", json={
       "email": context.email,
       "password": context.password
   })
   context.response = response


@then('the account with this data should be deleted')
def step_delete_success(context):
   assert context.response.status_code == 200
