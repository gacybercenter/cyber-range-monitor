
SessionAuth = SessionAuthority()


async def get_current_user(
    request: Request,
    response: Response,
    session_auth: SessionData = Depends(SessionAuth),
    db: AsyncSession = Depends(get_db)
) -> User:
    '''_summary_
    Gets the current user from the associated session from the Users table and 
    guarntees that the session is valid and that the client is not impersonating 
    another user.

    Keyword Arguments:
        session_data {SessionData} --  {Depends(SessionAuthSchema())})
        db {AsyncSession} -- _description_ (default: {Depends(get_db)})

    Raises:
        HTTPerroreption: 404 if the user is not found

    Returns:
        User
    '''
    auth = AuthService()
    existing_user = await auth.get_username(session_auth.username, db)

    session_signature = request.cookies.get(settings.SESSION_COOKIE)
    mapped_user = session_auth.client_identity.mapped_user
    if not existing_user:
        await SessionAuth.revokes(session_signature, response)
        raise HTTPInvalidSession(
            'Your session corresponds to a non-existent user, please login again'
        )
    elif mapped_user != 'Unknown' and mapped_user != existing_user.username:
        await SessionAuth.revokes(session_signature, response)
        raise HTTPInvalidSession(
            'Your session is not authorized under your current user.'
        )

    if existing_user.role != session_auth.role:
        await SessionAuth.revokes(session_signature, response)
        raise HTTPInvalidSession(
            'Your session has been terminated due to your security permissions changing'
        )

    return existing_user
