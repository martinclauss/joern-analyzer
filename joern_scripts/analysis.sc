// Print starting message to verify script execution
println("Starting analysis with Joern script...")

// Import core Joern libraries
import io.shiftleft.semanticcpg.language._
import org.json4s._
import org.json4s.native.Serialization
import org.json4s.native.Serialization.write
import org.json4s.native.JsonMethods._
import io.joern.joerncli.JoernVectors.formats
import java.io.File

// Helper functions for file operations
def writeJsonToFile[T](data: T, filePath: String)(implicit formats: Formats): Unit = {
  val writer = new java.io.PrintWriter(new java.io.File(filePath))
  try {
    // Convert to JValue first to handle large strings
    val json = Extraction.decompose(data)
    writer.write(compact(render(json)))
  } finally {
    writer.close()
  }
}

// Get the full method code by reading the file directly since joern truncates the .code at 1000 chars
def extractFunctions(): List[Map[String, Any]] = {
  cpg.method.map { method =>
    val code = method.file.name.headOption.map { fileName =>
      val file = new java.io.File(s"/app/$fileName")
      if (file.exists()) {
        val source = scala.io.Source.fromFile(file)
        try {
          val lines = source.getLines().toList
          val startLine = method.lineNumber.getOrElse(1)
          val endLine = method.lineNumberEnd.getOrElse(startLine)
          lines.slice(startLine - 1, endLine).mkString("\n")
        } finally {
          source.close()
        }
      } else {
        method.code
      }
    }.getOrElse(method.code)

    Map(
      "name" -> method.name,
      "file" -> method.file.name.headOption.getOrElse("<unknown>"),
      "lineNumber" -> method.lineNumber.getOrElse(-1),
      "code" -> code,
      "signature" -> method.signature
    )
  }.toList
}

def extractCallGraph(): List[Map[String, Any]] = {
  cpg.call.map { call =>
    Map(
      "name" -> call.name,
      "method" -> call.method.name,
      "file" -> call.file.name.headOption.getOrElse("<unknown>"),
      "lineNumber" -> call.lineNumber.getOrElse(-1)
    )
  }.toList
}

// Main execution
try {
  importCpg("/results/cpg.bin")
  
  // Use DefaultFormats with no custom serialization
  implicit val formats: Formats = DefaultFormats
  
  writeJsonToFile(extractFunctions(), "/results/functions.json")
  writeJsonToFile(extractCallGraph(), "/results/call_graph.json")
} catch {
  case e: Exception =>
    println(s"Error during analysis: ${e.getMessage}")
    throw e
}