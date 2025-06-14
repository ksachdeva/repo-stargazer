from a2a import types as a2a_types
from google.genai import types as genai_types


def convert_a2a_parts_to_genai(parts: list[a2a_types.Part]) -> list[genai_types.Part]:
    """Convert a list of A2A Part types into a list of Google Gen AI Part types."""
    return [convert_a2a_part_to_genai(part) for part in parts]


def convert_a2a_part_to_genai(part: a2a_types.Part) -> genai_types.Part:
    """Convert a single A2A Part type into a Google Gen AI Part type."""
    root_part = part.root
    if isinstance(root_part, a2a_types.TextPart):
        return genai_types.Part(text=root_part.text)
    if isinstance(root_part, a2a_types.FilePart):
        if isinstance(root_part.file, a2a_types.FileWithUri):
            return genai_types.Part(
                file_data=genai_types.FileData(
                    file_uri=root_part.file.uri,
                    mime_type=root_part.file.mimeType,
                )
            )
        if isinstance(root_part.file, a2a_types.FileWithBytes):
            return genai_types.Part(
                inline_data=genai_types.Blob(
                    data=root_part.file.bytes,
                    mime_type=root_part.file.mimeType,
                )
            )
        raise ValueError(f"Unsupported file type: {type(root_part.file)}")
    raise ValueError(f"Unsupported part type: {type(root_part)}")


def convert_genai_parts_to_a2a(parts: list[genai_types.Part]) -> list[a2a_types.Part]:
    """Convert a list of Google Gen AI Part types into a list of A2A Part types."""
    return [convert_genai_part_to_a2a(part) for part in parts if (part.text or part.file_data or part.inline_data)]


def convert_genai_part_to_a2a(part: genai_types.Part) -> a2a_types.Part:
    """Convert a single Google Gen AI Part type into an A2A Part type."""
    if part.text:
        return a2a_types.TextPart(text=part.text)
    if part.file_data:
        return a2a_types.FilePart(
            file=a2a_types.FileWithUri(
                uri=part.file_data.file_uri,
                mimeType=part.file_data.mime_type,
            )
        )
    if part.inline_data:
        return a2a_types.Part(
            root=a2a_types.FilePart(
                file=a2a_types.FileWithBytes(
                    bytes=part.inline_data.data,
                    mimeType=part.inline_data.mime_type,
                )
            )
        )
    raise ValueError(f"Unsupported part type: {part}")
