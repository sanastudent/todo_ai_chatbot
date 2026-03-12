#!/usr/bin/env python3
"""
Simple script to update the invoke_agent function with the correct pattern matching logic
"""
import re

# Read the entire file
with open('backend/src/services/agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new function body with the correct pattern matching order
new_function_body = '''
    try:
        # For now, implement basic natural language processing to detect task creation
        # This is a simple implementation - in a real system, this would call OpenAI/Anthropic
        # with MCP tools for proper function calling
        user_message = user_message.strip('"\'').lower()

        # DEBUG: Print what's being checked
        print(f"DEBUG: Checking message: '{user_message}'")

        # FIRST: Check for priority color help (look for phrases like "color mean", "red means")
        priority_color_help = (
            'color mean' in user_message or
            'red means' in user_message or
            'yellow means' in user_message or
            'green means' in user_message or
            'what do red' in user_message or
            'what do yellow' in user_message or
            'what do green' in user_message or
            'priority color' in user_message or
            'mean' in user_message and any(color in user_message for color in ['red', 'yellow', 'green'])
        )
        if priority_color_help:
            # Return color explanation
            color_explanation = (
                "Priority colors in the task manager system:\\n"
                "🔴 Red = High Priority\\n"
                "🟡 Yellow = Medium Priority\\n"
                "🟢 Green = Low Priority"
            )
            return color_explanation

        # SECOND: Check for search commands (look for "find ", "search ", "look for ")
        search_patterns = ['find ', 'search ', 'look for ']
        search_cmd = any(pattern in user_message for pattern in search_patterns)
        if search_cmd:
            # Determine if the user wants to filter by completion status
            completed_filter = None
            if any(phrase in user_message for phrase in [
                "pending", "not done", "not completed", "incomplete", "to do", "all tasks"
            ]):
                completed_filter = False
            elif any(phrase in user_message for phrase in [
                "completed", "done", "finished", "show completed"
            ]):
                completed_filter = True

            # Extract filtering and sorting parameters
            priority_filter = extract_priority_filter(user_message)
            tags_filter = extract_tags_filter(user_message)
            search_term = extract_search_term(user_message)
            sort_params = extract_sort_params(user_message)

            try:
                # Call the list_tasks MCP tool with the database session and filters
                tasks_result = await list_tasks(
                    user_id=user_id,
                    completed=completed_filter,
                    priority=priority_filter,
                    tags=tags_filter,
                    search_term=search_term,
                    sort_by=sort_params.get('sort_by'),
                    sort_order=sort_params.get('sort_order'),
                    db_session=db_session
                )

                # Format and return the tasks
                if tasks_result["success"]:
                    tasks = tasks_result["tasks"]

                    if not tasks:
                        return "No tasks found matching your search criteria."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "🔴 "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "🟡 "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "🟢 "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"✅ {task_entry}"
                        else:
                            task_entry = f"⭕ {task_entry}"
                        task_list.append(task_entry)

                    return "Here are the tasks matching your search:\\n" + "\\n".join(task_list)
                else:
                    return "I couldn't retrieve your tasks right now. Please try again."
            except Exception as e:
                logger.error(f"Error searching tasks: {str(e)}")
                return "Sorry, I couldn't search your tasks. Please try again."

        # THIRD: Check for tag operations (look for "add tag" AND "task" in same message)
        import re
        tag_operation = (
            ('add' in user_message and 'tag' in user_message and 'task' in user_message) or
            ('remove' in user_message and 'tag' in user_message and 'task' in user_message) or
            re.search(r'add\\s+\\w+\\s+tag\\s+to\\s+task\\s+\\d+', user_message) or
            re.search(r'remove\\s+\\w+\\s+tag\\s+from\\s+task\\s+\\d+', user_message)
        )

        if tag_operation:
            # This is a tag management command, not task creation
            task_to_update, new_title, new_description = extract_task_details_for_update(user_message)
            has_tag_pattern = task_to_update and ("_add_tag_" in task_to_update or "_remove_tag_" in task_to_update)
            if has_tag_pattern:
                try:
                    # Parse the special tag management format: "{task_number}_{operation}_{tag}"
                    parts = task_to_update.split("_")
                    if len(parts) >= 3 and parts[1] in ["add", "remove"]:
                        task_number = parts[0]
                        operation = parts[1]  # "add" or "remove"
                        tag = "_".join(parts[2:])  # Join any remaining parts in case tag had underscores

                        # Get all tasks to map by position
                        all_tasks_result = await list_tasks(user_id=user_id, completed=None, db_session=db_session)  # Get all tasks
                        all_tasks = all_tasks_result["tasks"]

                        # Convert the number to an index (1-based to 0-based)
                        task_idx = int(task_number) - 1

                        if 0 <= task_idx < len(all_tasks):
                            # Found the task by number
                            task_to_update_obj = all_tasks[task_idx]
                            task_id = task_to_update_obj["task_id"]

                            # Get current tags and modify them
                            # Tags are stored as JSON string, so we need to parse them
                            tags_json = task_to_update_obj.get("tags", "[]")
                            try:
                                current_tags = json.loads(tags_json) if tags_json else []
                            except (json.JSONDecodeError, TypeError):
                                current_tags = []

                            if operation == "add":
                                # Add the tag if it's not already present
                                if tag not in current_tags:
                                    current_tags.append(tag)
                                else:
                                    return f"Tag '{tag}' is already associated with task '{task_to_update_obj['title']}'."
                            elif operation == "remove":
                                # Remove the tag if it exists
                                if tag in current_tags:
                                    current_tags.remove(tag)
                                else:
                                    return f"Tag '{tag}' is not associated with task '{task_to_update_obj['title']}'. Cannot remove."

                            # Call the update_task MCP tool with the updated tags
                            update_result = await update_task(
                                user_id=user_id,
                                task_id=task_id,
                                tags=current_tags,
                                db_session=db_session
                            )

                            if operation == "add":
                                return f"I've added the tag '{tag}' to task '{task_to_update_obj['title']}'."
                            else:  # remove
                                return f"I've removed the tag '{tag}' from task '{task_to_update_obj['title']}'."
                        else:
                            return f"Could not find task number {task_idx + 1}. Please specify a number between 1 and {len(all_tasks)}."

                except Exception as e:
                    logger.error(f"Error managing tags: {str(e)}")
                    return f"Sorry, I couldn't manage the tags for that task. Error: {str(e)}"

        # FOURTH: Check for filter commands (look for messages starting with "show " or "filter ")
        filter_cmd = user_message.startswith('show ') or user_message.startswith('filter ')
        if filter_cmd:
            # Determine if the user wants to filter by completion status
            completed_filter = None
            if any(phrase in user_message for phrase in [
                "pending", "not done", "not completed", "incomplete", "to do", "all tasks"
            ]):
                completed_filter = False
            elif any(phrase in user_message for phrase in [
                "completed", "done", "finished", "show completed"
            ]):
                completed_filter = True

            # Extract filtering and sorting parameters
            priority_filter = extract_priority_filter(user_message)
            tags_filter = extract_tags_filter(user_message)
            search_term = extract_search_term(user_message)
            sort_params = extract_sort_params(user_message)

            try:
                # Call the list_tasks MCP tool with the database session and filters
                tasks_result = await list_tasks(
                    user_id=user_id,
                    completed=completed_filter,
                    priority=priority_filter,
                    tags=tags_filter,
                    search_term=search_term,
                    sort_by=sort_params.get('sort_by'),
                    sort_order=sort_params.get('sort_order'),
                    db_session=db_session
                )

                # Format and return the tasks
                if tasks_result["success"]:
                    tasks = tasks_result["tasks"]

                    if not tasks:
                        return "No tasks found matching your filter criteria."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "🔴 "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "🟡 "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "🟢 "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"✅ {task_entry}"
                        else:
                            task_entry = f"⭕ {task_entry}"
                        task_list.append(task_entry)

                    return "Here are the filtered tasks:\\n" + "\\n".join(task_list)
                else:
                    return "I couldn't retrieve your tasks right now. Please try again."
            except Exception as e:
                logger.error(f"Error filtering tasks: {str(e)}")
                return "Sorry, I couldn't filter your tasks. Please try again."

        # FIFTH: Check for sort commands (look for "sort" in message)
        sort_cmd = 'sort' in user_message
        if sort_cmd:
            # Extract sorting parameters
            sort_params = extract_sort_params(user_message)

            try:
                # Call the list_tasks MCP tool with the database session and sort parameters
                tasks_result = await list_tasks(
                    user_id=user_id,
                    completed=None,  # Get all tasks
                    priority=None,   # No priority filter
                    tags=None,       # No tags filter
                    search_term=None, # No search term
                    sort_by=sort_params.get('sort_by'),
                    sort_order=sort_params.get('sort_order'),
                    db_session=db_session
                )

                # Format and return the sorted tasks
                if tasks_result["success"]:
                    tasks = tasks_result["tasks"]

                    if not tasks:
                        return "You have no tasks to sort."

                    # Format tasks for display
                    task_list = []
                    for i, task in enumerate(tasks, 1):
                        # Get priority indicator
                        priority_indicator = ""
                        if task.get("priority"):
                            if task["priority"].lower() == "high":
                                priority_indicator = "🔴 "
                            elif task["priority"].lower() == "medium":
                                priority_indicator = "🟡 "
                            elif task["priority"].lower() == "low":
                                priority_indicator = "🟢 "

                        # Get tags
                        tags_display = ""
                        if task.get("tags"):
                            try:
                                import json
                                tags = json.loads(task["tags"]) if isinstance(task["tags"], str) else task["tags"]
                                if tags:
                                    tags_display = f" #{' #'.join(tags)}"
                            except:
                                pass

                        task_entry = f"{i}. {priority_indicator}{task['title']}{tags_display}"
                        if task.get("completed"):
                            task_entry = f"✅ {task_entry}"
                        else:
                            task_entry = f"⭕ {task_entry}"
                        task_list.append(task_entry)

                    sort_description = f"sorted by {sort_params.get('sort_by', 'default')} ({sort_params.get('sort_order', 'asc')})"
                    return f"Here are your tasks {sort_description}:\\n" + "\\n".join(task_list)
                else:
                    return "I couldn't retrieve your tasks right now. Please try again."
            except Exception as e:
                logger.error(f"Error sorting tasks: {str(e)}")
                return "Sorry, I couldn't sort your tasks. Please try again."

        # LAST: Check for task creation (look for "add" AND "task" in message)
        task_creation = 'add' in user_message and 'task' in user_message
        if task_creation:
            # Extract task details using the existing logic
            task_title, task_description = extract_task_details(user_message)

            # Extract priority and tags if present in the message
            priority = extract_priority_from_message(user_message)
            tags = extract_tags_from_message(user_message)

            # If we couldn't extract a title, use the original message as a fallback
            if not task_title:
                # Clean up the message to get a reasonable task title
                task_title = user_message.replace("add ", "").strip()

            try:
                # Call the add_task MCP tool with the database session, priority, and tags
                task_result = await add_task(
                    user_id=user_id,
                    title=task_title,
                    description=task_description,
                    priority=priority,
                    tags=tags,
                    db_session=db_session
                )

                # Check if task was already existing (duplicate prevention)
                if task_result.get("was_duplicate"):
                    response = f"'{task_title}' is already in your tasks."
                else:
                    response = f"I've added '{task_title}' to your tasks. Task ID: {task_result['task_id']}"

                return response
            except Exception as e:
                logger.error(f"Error adding task: {str(e)}")
                return f"Sorry, I couldn't add that task. Error: {str(e)}"

        # If none of the above patterns match, use fallback response
        # For now, we'll call the mock AI response as a fallback
        return await mock_ai_response(user_message)
'''

# Manually replace the function by finding the specific parts
start_marker = '# For now, implement basic natural language processing to detect task creation'
end_marker = ') -> str:'

# Split the content
parts = content.split(start_marker)
before_func = parts[0] + start_marker

# Find where the function ends (looking for the first return after try block that's not inside a nested block)
after_func = new_function_body + '\n' + content.split('return await mock_ai_response(user_message)')[1]

updated_content = before_func + after_func

# Write the updated content back to the file
with open('backend/src/services/agent.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("invoke_agent function has been updated with the correct pattern matching order!")