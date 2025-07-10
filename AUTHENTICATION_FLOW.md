# Authentication Flow Documentation

This document explains the authentication flow implemented for the Chargebee KYB Risk Assessment platform.

## Overview

The authentication system uses Supabase for user management and ensures only Chargebee employees (with @chargebee.com emails) can access the platform.

## Login Flow

1. **Email Validation**: 
   - Only @chargebee.com email addresses are accepted
   - Invalid domains show error: "Please use a valid @chargebee.com email address"

2. **User Existence Check**:
   - System checks if user exists in Supabase profiles table
   - If user doesn't exist: Shows "No account found with this email. Please sign up first."
   - Automatically redirects to signup page after 2 seconds

3. **Email Verification Check**:
   - If user exists but hasn't verified their email: Shows "Please verify your email before logging in. Check your inbox for the verification link."
   - User must click the verification link in their email before they can login

4. **Authentication**:
   - If user exists and email is verified, authentication proceeds
   - On successful login, user is redirected to the dashboard

## Signup Flow

1. **Email Validation**:
   - Only @chargebee.com email addresses are accepted
   - Invalid domains show error immediately

2. **Duplicate Check**:
   - System checks if email already exists in Supabase
   - If exists: Shows "An account with this email already exists. Please login instead."
   - Automatically switches to login mode
   - On blur of email field, checks existence and prompts user to switch to login

3. **Account Creation**:
   - Password must be at least 6 characters
   - Full name is required
   - After successful signup:
     - In production: Shows "Please check your email to validate the link we sent, then come back and login."
     - In development mode: Auto-login after signup

4. **Email Verification**:
   - Supabase sends verification email automatically
   - User must click the link to verify their email
   - After verification, user can login normally

## Security Features

- **Domain Restriction**: Only @chargebee.com emails allowed
- **Email Verification**: Required before first login
- **Password Requirements**: Minimum 6 characters
- **Session Management**: Tokens stored securely in localStorage
- **Auto-logout**: On unauthorized access or expired sessions

## Development Mode

In development mode (`ENVIRONMENT=development`):
- Email verification is bypassed
- Auto-login after signup
- Test credentials work for specific test accounts

## Error Handling

The system provides clear, user-friendly error messages:
- Wrong domain: Suggests using @chargebee.com email
- No account: Redirects to signup
- Unverified email: Asks to check email
- Wrong password: Shows invalid credentials error

## Technical Implementation

- **Frontend**: React with API service layer
- **Backend**: FastAPI with Supabase Python client
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth with email verification