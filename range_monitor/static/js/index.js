import { typer } from './effects/typer.js';




$(document).ready(function () {
	

});



function heroAnimation() {
	const typingInfo = {
		$heroTypedTag : $("#heroTypedText"),
		userName : $heroTypedTag.data("username"),
	}
	const animator = new TypingAnimation(typingInfo.$heroTypedTag);

}