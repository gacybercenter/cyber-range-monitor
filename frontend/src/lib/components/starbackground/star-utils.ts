export type Star = {
	left: number;
	top: number;
	size: number;
	delay: number;
	progress: number;
	speed: number;
};

export const createStar = (): Star => {
	const left = Math.floor(Math.random() * 100);
	const top = Math.floor(Math.random() * 100);
	const size = Math.floor(Math.random() * 3) + 1;
	const delay = Math.random() * 15;
	const progress = 0;
	const speed = 0.005 + Math.random() * 0.003;

	return { left, top, size, delay, progress, speed };
};

export const moveAndTwinkleStar = (
	{ progress, left, top, size }: Star,
	width: number,
	height: number
) => {
	let opacity = 0.5;
	if (progress < 0.1) {
		opacity = (progress / 0.1) * 0.5;
	} else if (progress > 0.9) {
		opacity = ((1 - progress) / 0.1) * 0.5;
	}

	const startX = (left / 100) * width;
	const startY = (top / 100) * height;
	const moveX = progress * 20;
	const moveY = -progress * 20;

	return {
		x: startX + moveX,
		y: startY + moveY,
		radius: size / 2,
		opacity
	};
};
