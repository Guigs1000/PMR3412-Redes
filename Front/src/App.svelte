<script>
	export let name;
	import {onMount} from "svelte";
	let inputText = "";
	let name_set = 0;
	let data = {};
	let messageInput;
	let messages = [];

	onMount(() => {
		messageInput.focus();
	});
	const ws = new WebSocket("ws://localhost:4444");
	ws.onopen = function(){
		console.log("WebSocket client Connected");
	}
	ws.onmessage = function(e) {
		data = JSON.parse(e.data);
		messages = [...messages, data.message];
	}
	function handleClick(){
		let output;
		let message;
		if(data.message.slice(0,16) == "Nome registrado!"){
			name_set = 1;
		}
		if (name_set == 0){
			output = {"action": "public_message", "message": inputText};
		} else if (inputText.charAt(0) == "/") {
			let receiver = inputText.split(" ")[0].substring(1);
			let msg = inputText.substr(inputText.indexOf(" ") + 1);
			output = {"action": "private_message", "message": msg, "receiver": receiver};
			message = "Você (" + receiver +") >> " + msg; 
			messages = [...messages, message];
		} else {
			output = {"action": "public_message", "message": inputText};
			message = "Você >> " + inputText;
			messages = [...messages, message];
		}
		ws.send(JSON.stringify(output));
		inputText = "";
	}
</script>

<main>
	<h1>{name}!</h1>
	<p>
		Bem vindo ao chat Websockets! 
	</p>
	<div class="chatbox">
		{#each messages as message}
			<p>{message}</p>
		{/each}	
	</div>
	<form class="inputbox">
		<input type="text" bind:this={messageInput} bind:value={inputText}/>
		<button type="submit" on:click|preventDefault={handleClick}>Send</button>
	</form>

</main>

<style>
	* {
	box-sizing: border-box;
	}
	main {
		width: calc(100% - 30px);
		text-align: center;
		padding: 1em;
		max-width: 1240px;
		margin: 0 auto;
	}
	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}
	.chatbox {
		width: 100%;
		height: 50vh;
		padding: 0 1cm;
		text-align: left;
		background-color: #eee;
		overflow-y: scroll;
		overscroll-behavior-y: contain;
		scroll-snap-type: y proximity;
	}
	.chatbox p{
		margin-top: 0.5cm;
		margin-bottom: 0;
		padding-bottom: 0.5cm;
	}
	.chatbox > p:last-child{
		scroll-snap-align: end;
	}
	.inputbox{
		display: flex;
		margin-top: 0.5cm;
	}
	.inputbox input{
		flex-grow: 1;
	}
</style>
