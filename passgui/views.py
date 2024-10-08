import os
from django.conf import settings
from django.shortcuts import render, redirect

def single_page_view(request):
    if request.method == 'POST':
        # Check if Pass 1 is triggered
        if 'clear_button' in request.POST: 
            # Clear session data
            request.session.clear()
            return redirect('passgui:assembler')
        
        if 'pass1_button' in request.POST:
            # Get the uploaded input file and optab file for Pass 1
            input_file = request.FILES.get('inputFile')
            optab_file = request.FILES.get('optabFile')

            if input_file and optab_file:  # Ensure files are uploaded
                # Read OPTAB file content into memory
                optab_lines = optab_file.read().decode('utf-8').splitlines()
                OPTAB = {line.split()[0]: line.split()[1] for line in optab_lines}

                # Call Pass 1 logic
                input_lines = input_file.read().decode('utf-8').splitlines()
                intermediate_content, symtab_content, program_length = pass1_logic(input_lines, OPTAB)

                # Store results in session
                request.session['intermediate_content'] = intermediate_content
                request.session['symtab_content'] = symtab_content
                request.session['program_length'] = program_length
                request.session['optab_content'] = optab_lines  # Store optab for Pass 2

                # Indicate that Pass 1 has been completed
                request.session['pass1_done'] = True
                request.session.modified = True

        # Check if Pass 2 is triggered
        elif 'pass2_button' in request.POST:
            # Retrieve intermediate, symtab, and optab content from session
            intermediate_content = request.session.get('intermediate_content')
            symtab_content = request.session.get('symtab_content')
            optab_lines = request.session.get('optab_content')

            # Ensure that symtab_content is not None
            if symtab_content is None:
                # You can handle this scenario gracefully, maybe redirect or show an error message
                return render(request, 'single_page.html', {
                    'error': 'Pass 1 has not been completed. Please run Pass 1 first.',
                })

            # Parse the OPTAB to a dictionary
            optab = {line.split()[0]: line.split()[1] for line in optab_lines}

            # Call Pass 2 logic
            object_code = pass2_logic(intermediate_content, symtab_content, optab)

            # Store the result of Pass 2 in session
            request.session['object_code'] = object_code
            request.session.modified = True


    # Get all necessary data to render the page
    intermediate_content = request.session.get('intermediate_content', '')
    symtab_content = request.session.get('symtab_content', '')
    program_length = request.session.get('program_length', '')
    object_code = request.session.get('object_code', '')
    pass1_done = request.session.get('pass1_done', False)

    return render(request, 'single_page.html', {
        'intermediate': intermediate_content,
        'symtab': symtab_content,
        'length': program_length,
        'object_code': object_code,
        'pass1_done': pass1_done,
    })




def pass1_logic(input_lines, OPTAB):
    SYMTAB = {}
    intermediate_content = ""
    symtab_content = ""
    start_address = 0
    program_name = ""
    program_length = 0
    LOCCTR = 0

    for line in input_lines:
        line_parts = line.split()

        if len(line_parts) == 3:
            label, opcode, operand = line_parts
        elif len(line_parts) == 2:
            label, opcode = line_parts
            operand = ''
        else:
            continue

        if opcode == "START":
            start_address = int(operand, 16)
            LOCCTR = start_address
            program_name = label
            intermediate_content += f"\t{line.strip()}\n"
        elif opcode == "END":
            intermediate_content += f"{LOCCTR:04X}\t{line.strip()}\n"
            program_length = LOCCTR - start_address
        else:
            intermediate_content += f"{LOCCTR:04X}\t{line.strip()}\n"

            if label and label != '-':
                if label in SYMTAB:
                    raise ValueError(f"Error: Symbol {label} already exists in SYMTAB.")
                else:
                    SYMTAB[label] = LOCCTR
                    symtab_content += f"{label}\t{LOCCTR:04X}\n"

            if opcode in OPTAB:
                LOCCTR += 3
            elif opcode == "WORD":
                LOCCTR += 3
            elif opcode == "RESW":
                LOCCTR += 3 * int(operand)
            elif opcode == "RESB":
                LOCCTR += int(operand)
            elif opcode == "BYTE":
                LOCCTR += len(operand) - 3

    return intermediate_content, symtab_content, f"{program_length:04X}"


def pass2_logic(intermediate_content, symtab_content, optab):
    # Read SYMTAB into a dictionary
    symtab = {}
    for line in symtab_content.splitlines():
        if line.strip():  # Avoid processing empty lines
            symbol, address = line.split()
            symtab[symbol] = int(address, 16)

    # Parse the intermediate content to generate object code
    object_code_lines = []
    output_lines = []

    # Split intermediate content into lines for processing
    lines = intermediate_content.splitlines()

    header_record = ''
    text_record = ''
    end_record = ''
    
    #program_name = "PROG"
    start_address = 0
    program_length = 0
    text_start_address = ''
    text_record_data = []
    text_record_length = 0

    for line in lines:
        parts = line.split('\t')
        if len(parts) < 3:
            continue

        locctr = parts[0].strip()
        label = parts[1].strip()
        opcode = parts[2].strip()
        operand = parts[3].strip() if len(parts) > 3 else ''

        # Process the opcode and object code generation
        if opcode == "START":
            program_name = label
            start_address = int(operand, 16)
            header_record = f"H^{program_name}^{start_address:06X}^0000\n"
            text_start_address = f"{start_address:06X}"

        elif opcode in optab:
            obj_code = optab[opcode]

            if operand in symtab:
                address = symtab[operand]
                obj_code_line = f"{obj_code}{address:04X}"
            else:
                obj_code_line = f"{obj_code}0000"

            object_code_lines.append(obj_code_line)
            text_record_data.append(obj_code_line)
            text_record_length += len(obj_code_line) // 2  # Each byte is 2 hex digits

        elif opcode == "WORD":
            value = int(operand)
            obj_code_line = f"{value:06X}"
            object_code_lines.append(obj_code_line)
            text_record_data.append(obj_code_line)
            text_record_length += 3  # WORD is 3 bytes

        elif opcode == "BYTE":
            if operand.startswith("C'"):
                byte_values = ''.join([f"{ord(c):02X}" for c in operand[2:-1]])
            elif operand.startswith("X'"):
                byte_values = operand[2:-1]
            object_code_lines.append(byte_values)
            text_record_data.append(byte_values)
            text_record_length += len(byte_values) // 2

        elif opcode == "RESW" or opcode == "RESB":
            # When a reservation occurs, flush the current text record if any
            if text_record_data:
                text_record = f"T^{text_start_address}^{text_record_length:02X}^{'^'.join(text_record_data)}\n"
                output_lines.append(text_record)
                text_record_data = []
                text_record_length = 0

            # Reset start address for the next text record after a reserved memory section
            text_start_address = f"{int(locctr, 16):06X}"

        elif opcode == "END":
            end_record = f"E^{start_address:06X}\n"
            break

    # Create the final text record if data remains
    if text_record_data:
        text_record = f"T^{text_start_address}^{text_record_length:02X}^{'^'.join(text_record_data)}\n"
        output_lines.append(text_record)

    program_length = int(locctr, 16) - start_address
    header_record = header_record.replace("^0000", f"^{program_length:06X}")

    # Combine header, text, and end records
    object_code = header_record + ''.join(output_lines) + end_record
    return object_code
