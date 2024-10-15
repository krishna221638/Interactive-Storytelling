// import React, { useState } from "react";
// import axios from "axios";
// import "./App.css";

// function App() {
//   const [storyText, setStoryText] = useState("");
//   const [enhancedStory, setEnhancedStory] = useState([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [errorMessage, setErrorMessage] = useState("");

//   // Handle form submission to send story text to the backend
//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setErrorMessage("");
//     setIsLoading(true);

//     try {
//       // Send the story text to the FastAPI backend
//       const response = await axios.post(
//         "http://127.0.0.1:8000/generate_storybook",
//         {
//           story: storyText,
//         }
//       );

//       // Set the enhanced story and images in state
//       setEnhancedStory(response.data.images ?? []);

//       setIsLoading(false);
//     } catch (error) {
//       console.error("Error generating storybook:", error);
//       setErrorMessage("Failed to generate storybook. Please try again.");
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="App" style={{ padding: "20px" }}>
//       <h1>Storybook Creator</h1>
//       <form onSubmit={handleSubmit}>
//         <textarea
//           value={storyText}
//           onChange={(e) => setStoryText(e.target.value)}
//           placeholder="Enter your story text here..."
//           rows="10"
//           cols="50"
//           style={{ marginBottom: "10px" }}
//         />
//         <br />
//         <button
//           type="submit"
//           style={{ padding: "10px 20px", fontSize: "16px" }}
//         >
//           Generate Story
//         </button>
//       </form>
//       {!isLoading && enhancedStory.length === 0 && (
//         <p>No images generated yet. Submit a story to see the result.</p>
//       )}

//       {/* Display loader while generating story */}
//       {isLoading && <p>Generating your storybook... Please wait.</p>}

//       {/* Display error message if any */}
//       {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

//       {/* Display generated storybook with images and enhanced text */}
//       {enhancedStory.length > 0 && (
//         <div>
//           <h2>Generated Storybook</h2>
//           {enhancedStory.map((item, index) => (
//             <div key={index} style={{ marginBottom: "30px" }}>
//               <h3>Page {index + 1}</h3>
//               <p style={{ fontStyle: "italic" }}>{item.text}</p>
//               <img
//                 src={`http://127.0.0.1:8000/static/${item.image_path
//                   .split("/")
//                   .pop()}`}
//                 alt={`Storybook page ${index + 1}`}
//                 style={{ maxWidth: "600px", marginTop: "10px" }}
//               />
//             </div>
//           ))}
//         </div>
//       )}
//     </div>
//   );
// }

//export default App;

import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [storyText, setStoryText] = useState("");
  const [enhancedStory, setEnhancedStory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Handle form submission to send story text to the backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setIsLoading(true);

    try {
      // Send the story text to the FastAPI backend
      const response = await axios.post(
        "http://127.0.0.1:8000/generate_storybook",
        {
          story: storyText,
        }
      );

      // Set the enhanced story and images in state
      setEnhancedStory(response.data.images ?? []);
      setIsLoading(false);
    } catch (error) {
      console.error("Error generating storybook:", error);
      setErrorMessage("Failed to generate storybook. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="App" style={{ padding: "20px" }}>
      <h1>Storybook Creator</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={storyText}
          onChange={(e) => setStoryText(e.target.value)}
          placeholder="Enter your story text here..."
          rows="10"
          cols="50"
          style={{ marginBottom: "10px" }}
        />
        <br />
        <button
          type="submit"
          style={{ padding: "10px 20px", fontSize: "16px" }}
        >
          Generate Story
        </button>
      </form>
      {!isLoading && enhancedStory.length === 0 && (
        <p>No images generated yet. Submit a story to see the result.</p>
      )}

      {/* Display loader while generating story */}
      {isLoading && <p>Generating your storybook... Please wait.</p>}

      {/* Display error message if any */}
      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      {/* Display generated storybook with images and enhanced text */}
      {enhancedStory.length > 0 && (
        <div>
          <h2>Generated Storybook</h2>
          {enhancedStory.map((item, index) => (
            <div key={index} style={{ marginBottom: "30px" }}>
              <h3>Page {index + 1}</h3>
              <p style={{ fontStyle: "italic" }}>{item.text}</p>
              <img
                src={`http://127.0.0.1:8000/static/${item.image_path
                  .split("/")
                  .pop()}`}
                alt={`Storybook page ${index + 1}`}
                style={{ maxWidth: "600px", marginTop: "10px" }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
