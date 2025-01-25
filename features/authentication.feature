Feature: User Authentication and Password Reset

     Scenario: User Registration
       Given the user provides valid email and password
       When the user registers
       Then the user receives a verification email
       Then the user confirms the email

     Scenario: User Login
       Given the user has registered and verified email
       When the user attempts to log in with wrong password
       Then the user should failed log in
       When the user attempts to log in with correct password
       Then the user should successfully log in

     Scenario: Password Reset Request
       Given the user has registered verified email and old password
       When the user requests a password reset
       Then the user should receive a verification code via email
       Then the user confirms the verification code

     Scenario: Password Reset Confirmation
       Given the user has registered verified email, new_password and verification code
       When the user confirms the password reset with the new password
       Then the user's password should be successfully changed

     Scenario: User Delete Account
       Given the user provides email and password
       When the user wants to delete an account using incorrect data
       Then an error should return stating that the data is incorrect
       When the user wants to delete an account using correct data
       Then the account with this data should be deleted
