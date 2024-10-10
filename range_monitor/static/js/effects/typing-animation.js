// static/js/components/typing-animation.js

export class TypingAnimation {
	/**
	 * Creates a typing animation given at least a jQuery element
	 * typingSpeed and delay are optional
	 * @param {*} $element
	 * @param {*} typingSpeed (default=150)
	 * @param {*} delay (default=1000)
	 */
	constructor($element, typingSpeed = 150, delay = 1000) {
		this.$element = $element;
		this.typingSpeed = typingSpeed;
		this.delay = delay;
		checkTypingAnimation(this);
		this.$element.addClass("typed-text");
	}
	/**
	 * Types a single message to the corresponding
	 * element when it is visible in the viewport
	 * @param {*} text
	 */
	async typeMessage(text) {
		animateWhenVisible(this.$element[0], async () => {
			await tryToType(this, text);
		});
	}
	/**
	 * Types a list of string messages to the element
	 * with a specified delay between each message 
	 * when it is visible in the viewport
	 * @param {*} messages 
	 * @param {*} messageDelay (default=1000) 
	 */
	async typeMessages(messages, messageDelay = 1000) {
		messages.forEach(async function (message) {
			await this.typeMessage(message);
			await new Promise((resolve) => setTimeout(resolve, messageDelay));
		});
	}
}

class TypingAnimationError extends Error {
	constructor(message) {
		super(message);
		this.name = 'TypingAnimationError';
	}
}

function animateWhenVisible(element, callback) {
	const watcher = new IntersectionObserver((entries, observer) => {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
				callback();
				observer.unobserve(entry.target);
			}
		});
	});
	watcher.observe(element);
}

function validateTyper(typer) {
	const validNum = (num) => typeof num === "number" && num > 0;
	if (!typer.$element.length) {
		return [false, "The element with the provided ID does not exist."];
	}
	if (!validNum(typer.typingSpeed) || !validNum(typer.delay)) {
		return [false, "The typing speed and delay must be positive numbers."];
	}
	return [true, null];
}

function checkTypingAnimation(typer) {
	const [isValid, error] = validateTyper(typer);
	if (!isValid) {
		throw new TypingAnimationError(error);
	}
}

function tryToType(typer, text) {
	return new Promise((resolve) => {
		typer.$element.empty();
		let i = 0;
		const type = () => {
			if (i < text.length) {
				console.log(text);
				typer.$element.text((_, oldText) => oldText + text.charAt(i));
				i++;
				setTimeout(type, typer.typingSpeed);
			} else {
				resolve(); 
			}
		};
		setTimeout(type, typer.delay);
	});
};