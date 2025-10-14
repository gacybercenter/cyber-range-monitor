import type { Cookies, RequestEvent } from '@sveltejs/kit';
import type { RefreshRequest, TokenClaim } from './api/client';
import { env } from '$env/dynamic/private';
import axios from 'axios';

