import { NextResponse } from "next/server";
import OpenAI from "openai";



const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

export async function GET(request: Request) {
    return new Response("Hello, Next.js!");
}


export async function POST(request: Request) {
    const { userText } = await request.json();
    const completion = await openai.chat.completions.create({
        messages: [{ role: 'user', content: userText }],
        model: 'gpt-3.5-turbo',
    }); 

    const aiMessage = completion.choices[0].message?.content;
    console.log(aiMessage);
    return NextResponse.json(
        {
            message: aiMessage
        },
        { status: 200 }
    );
}




// import { useEffect, useState } from "react";


// export async function App() {
//   const [messsage , setMesssage ] = useState(0)
//   useEffect(()=> {
//     fetch("")
//     .then((response) => response.json())
//     .then((data) => {
//       setMesssage(data.messsage)
//     })
//   }, [])
//   return <div>{messsage}</div> ;
// }