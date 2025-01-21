# Tests

## Auth Routes

## User Routes

### /user (root)

**Create User [POST]**

- [ ] is admin protected
- [ ] Unique user names are enforced

**Read All Users [GET]**

- [ ] Ensure that the role based read works
      users can only read user less than or equal to the permission set

### /user/{user_id}

**Update user [PUT]**

- Add test case for when an admin is trying to update their own role; that could be an edge case: (e.g) _(if reading_user is admin and update_req.role) raise forbidden_
- [ ] Admin Protected

**Read User By ID [GET]**

- [ ] Requires OAuth

- [ ] _"No read up"_ users cannot read above the set permission level

**Delete User [DELETE]**

- [ ] Admin Required

- [ ] User cannot delete themselves

### /user/details

**Read All User Details [GET]**

- [ ] Admin protected

### /user/details/{user_id}

- [ ] Admin Protected

## Datasource Routes





## Log Routes

## Auth Routes
