const defaults = {
	admin: {
		username: "Admin",
		role: "admin",
		password_hash:
			"$2b$12$/8cEqI6aa5kjK/fahhUdYeLu.ZtGw2hCkd.e290bdn0akWdddS8RC",
	},
	readonly: {
		username: "ReadOnlyUser",
		role: "read_only",
		password_hash:
			"$2b$12$YwN3jmlf/1gOSMHNSaYw4eCtS3BnjjJw4bfovdk0x96Um64ekUYDq",
	},
	user: {
		username: "DefaultUser",
		role: "user",
		password_hash:
			"$2b$12$HkIJVPfA3pFlV0JNYcX/CuUTAnuNW.0ijWVPm5xGG8DTh9FzzGaLS",
	},
};

const refreshDisplay = document.getElementById("refreshToken");
const accessDisplay = document.getElementById("accessToken");

const revokeBtn = document.getElementById("revoke");
const refreshBtn = document.getElementById("refresh");
const responseBtn = document.getElementById("responseDump");

const form = document.getElementById("login");

const getFormFields = () => {
	return [
		document.getElementById("username"),
		document.getElementById("password"),
	];
};

function FormDefaults() {
	document.querySelectorAll(".form-fill").forEach((btn) => {
		const target = btn.getAttribute("data-for");
		const targetLogin = defaults[target];
		btn.addEventListener("click", () => {
			const [username, password] = getFormFields();
			username.value = targetLogin.username;
			password.value = "password";
		});
	});
}



document.addEventListener("DOMContentLoaded", () => {
	FormDefaults();
});
