# Editing a live Confluence page

Read this before you change a Confluence page that already has content.
A new or empty page can take Markdown; a live page cannot.

## Why Markdown breaks live pages

`confluence_update_page` with Markdown replaces the whole body.
That wipes expand and other macros, the editor's `local-id` attributes, layout settings, and any edits people made in the browser since your last read.

## Steps

1. Fetch the page fresh with `confluence_get_page` and `convert_to_markdown=false`, just before you edit.
   Save the storage XHTML and note the version number.
   Done when you hold the storage body and version of the current page.
2. Make surgical string edits to that storage body: change only the text, cells or elements the task names.
   Wrap new collapsible content in an `expand` macro copied from one already on the page.
   Done when a text diff against the saved body shows only the intended changes, and the macro and `local-id` counts match, plus any you added.
3. Re-check the version (a `confluence_search` on the title returns it). If it moved, stop and redo step 1.
4. Publish with `content_format: storage`, and always pass `page_width` with the page's current value.
   The update resets an omitted width to fixed.
   `content_file` must sit under the session's working directory; paths outside it fail as path traversal.
5. Read the page back and compare its text, macro count, `local-id` count and `page_width` with what you sent.
   Done when all four match. Confluence may reorder macro parameters; that difference is cosmetic.
